import os

API_KEY = os.getenv("API_KEY", "changeme")
MAX_SCAN_SECONDS = int(os.getenv("MAX_SCAN_SECONDS", "900"))  # default 15 minutes
JOB_RETENTION_SECONDS = int(os.getenv("JOB_RETENTION_SECONDS", "86400"))  # how long results live in memory
