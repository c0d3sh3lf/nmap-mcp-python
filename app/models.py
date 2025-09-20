from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# === Scan models ===
class ScanRequest(BaseModel):
    target: str = Field(..., description="IP or hostname to scan")
    args: Optional[List[str]] = Field(default_factory=list, description="Additional nmap args (e.g. ['-sV','-p','80,443'])")
    max_seconds: Optional[int] = Field(None, description="Override default max runtime for this scan (seconds)")

class JobStatus(BaseModel):
    job_id: str
    target: str
    status: str  # queued | running | done | error
    created_at: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None

class ScanResult(BaseModel):
    job_id: str
    raw_xml: Optional[str] = None
    parsed: Optional[Dict[str, Any]] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None

# === Auth models ===
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiry in seconds")

class RefreshRequest(BaseModel):
    refresh_token: str
