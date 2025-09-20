import os

# === App general ===
MAX_SCAN_SECONDS = int(os.getenv("MAX_SCAN_SECONDS", "900"))
JOB_RETENTION_SECONDS = int(os.getenv("JOB_RETENTION_SECONDS", "86400"))

# === Auth config ===
# Minimum: set a strong SECRET_KEY and your login credentials
SECRET_KEY = os.getenv("SECRET_KEY", "SAg1bVGhzkvB2FvxjEoRfcKE323Xw1gR")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))      # default 15 minutes
REFRESH_TOKEN_EXPIRE_HOURS = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS", "24"))        # default 24 hours

# Very simple credential source (you can wire to real IdP later)
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "admin123")  # store secrets via env/secret manager in prod
