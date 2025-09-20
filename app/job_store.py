from typing import Dict, Optional
from .models import JobStatus, ScanResult
import time
import threading

class JobStore:
    def __init__(self):
        self._jobs: Dict[str, JobStatus] = {}
        self._results: Dict[str, ScanResult] = {}
        self._lock = threading.Lock()

    def add_job(self, job: JobStatus):
        with self._lock:
            self._jobs[job.job_id] = job

    def update_job(self, job_id: str, **kwargs):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for k, v in kwargs.items():
                setattr(job, k, v)
            self._jobs[job_id] = job

    def get_job(self, job_id: str) -> Optional[JobStatus]:
        return self._jobs.get(job_id)

    def list_jobs(self):
        return list(self._jobs.values())

    def set_result(self, job_id: str, result: ScanResult):
        with self._lock:
            self._results[job_id] = result

    def get_result(self, job_id: str) -> Optional[ScanResult]:
        return self._results.get(job_id)

job_store = JobStore()
