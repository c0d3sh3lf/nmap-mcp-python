import time
import uuid
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ScanRequest, JobStatus, ScanResult,
    LoginRequest, TokenPair, RefreshRequest
)
from .job_store import job_store
from .nmap_runner import run_nmap_blocking
from .config import AUTH_USERNAME, AUTH_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES
from .auth import create_access_token, create_refresh_token, decode_token
from .jwt_middleware import JWTAuthMiddleware

app = FastAPI(
    title="MCP Nmap FastAPI Server",
    version="0.2.0",
    description="Run nmap scans via REST API (JWT-protected)."
)

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT middleware: protect everything except public paths
app.add_middleware(
    JWTAuthMiddleware,
    public_paths=["/health"]
)

@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}

# === Auth endpoints ===
@app.post("/auth/login", response_model=TokenPair, tags=["auth"])
async def login(body: LoginRequest):
    if body.username != AUTH_USERNAME or body.password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(subject=body.username)
    refresh = create_refresh_token(subject=body.username)
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@app.post("/auth/refresh", response_model=TokenPair, tags=["auth"])
async def refresh_token(body: RefreshRequest):
    import jwt
    try:
        claims = decode_token(body.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if claims.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    subject = claims.get("sub")
    access = create_access_token(subject=subject)
    # You can choose whether to rotate refresh here; we’ll keep the old one valid until it expires.
    return TokenPair(
        access_token=access,
        refresh_token=body.refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

# === Scan endpoints (protected by JWT middleware) ===
@app.post("/scan")
async def start_scan(
    scan_req: ScanRequest,
    background: BackgroundTasks,
    sync: Optional[bool] = Query(False, description="If true, wait for scan to complete (not recommended for long scans)")
):
    target = scan_req.target.strip()
    if not target:
        raise HTTPException(400, "target is required")

    job_id = str(uuid.uuid4())
    now = time.time()
    job = JobStatus(
        job_id=job_id,
        target=target,
        status="queued",
        created_at=now
    )
    job_store.add_job(job)

    timeout_seconds = scan_req.max_seconds if scan_req.max_seconds else None
    args = scan_req.args or []

    # Synchronous worker for BackgroundTasks
    def _run_and_store_sync():
        job_store.update_job(job_id, status="running", started_at=time.time())
        exit_code, raw_xml, parsed, error = run_nmap_blocking(target, args, timeout_seconds)
        finished_at = time.time()
        job_store.update_job(
            job_id,
            status="done" if exit_code == 0 else "error",
            finished_at=finished_at,
            exit_code=exit_code,
            error=error
        )
        result = ScanResult(
            job_id=job_id,
            raw_xml=raw_xml,
            parsed=parsed,
            exit_code=exit_code,
            error=error
        )
        job_store.set_result(job_id, result)

    if sync:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _run_and_store_sync)
        return JSONResponse(
            status_code=200,
            content={"job_id": job_id, "status": job_store.get_job(job_id).status}
        )
    else:
        background.add_task(_run_and_store_sync)
        return {"job_id": job_id, "status": "queued"}

@app.get("/scan/{job_id}")
async def get_job(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job

@app.get("/scan/{job_id}/result")
async def get_result(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    result = job_store.get_result(job_id)
    if not result:
        if job.status in ("queued", "running"):
            return {"status": job.status, "message": "result not ready"}
        return {"status": job.status, "message": "no result"}
    return {
        "status": job.status,
        "exit_code": result.exit_code,
        "error": result.error,
        "parsed": result.parsed,
        "raw_xml": result.raw_xml
    }
