import time
import uuid
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import ScanRequest, JobStatus, ScanResult
from .job_store import job_store
from .nmap_runner import run_nmap_blocking
from .config import API_KEY, MAX_SCAN_SECONDS

app = FastAPI(title="MCP Nmap FastAPI Server", version="0.1.0", description="Run nmap scans via REST API (use only with authorization)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(request: Request):
    header_key = request.headers.get("x-api-key")
    if not header_key or header_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}

@app.post("/scan", dependencies=[Depends(verify_api_key)])
async def start_scan(scan_req: ScanRequest, background: BackgroundTasks, sync: Optional[bool] = Query(False, description="If true, wait for scan to complete (not recommended for long scans)")):
    """
    Start an nmap scan. By default the scan runs in background and returns job_id.
    Pass sync=true to wait for completion (blocking).
    """
    # Basic validation (you can expand)
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

    timeout_seconds = scan_req.max_seconds if scan_req.max_seconds else MAX_SCAN_SECONDS

    async def _run_and_store():
        # update job running
        job_store.update_job(job_id, status="running", started_at=time.time())
        exit_code, raw_xml, parsed, error = await asyncio.get_event_loop().run_in_executor(
            None, run_nmap_blocking, target, scan_req.args or [], timeout_seconds
        )
        finished_at = time.time()
        job_store.update_job(job_id, status="done" if exit_code == 0 else "error", finished_at=finished_at, exit_code=exit_code, error=error)
        result = ScanResult(
            job_id=job_id,
            raw_xml=raw_xml,
            parsed=parsed,
            exit_code=exit_code,
            error=error
        )
        job_store.set_result(job_id, result)

    if sync:
        # run synchronously (blocks)
        await _run_and_store()
        return JSONResponse(status_code=200, content={"job_id": job_id, "status": job_store.get_job(job_id).status})
    else:
        # schedule in background
        background.add_task(asyncio.ensure_future, _run_and_store())
        return {"job_id": job_id, "status": "queued"}

@app.get("/scan/{job_id}", dependencies=[Depends(verify_api_key)])
async def get_job(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job

@app.get("/scan/{job_id}/result", dependencies=[Depends(verify_api_key)])
async def get_result(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    result = job_store.get_result(job_id)
    if not result:
        if job.status in ("queued", "running"):
            return {"status": job.status, "message": "result not ready"}
        return {"status": job.status, "message": "no result"}
    # return both parsed JSON and raw XML
    return {
        "status": job.status,
        "exit_code": result.exit_code,
        "error": result.error,
        "parsed": result.parsed,
        "raw_xml": result.raw_xml
    }
