import time
import jwt
from typing import Optional, Dict, Any
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS

def _now() -> int:
    return int(time.time())

def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    iat = _now()
    exp = iat + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    payload = {
        "sub": subject,
        "type": "access",
        "iat": iat,
        "exp": exp,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    iat = _now()
    exp = iat + REFRESH_TOKEN_EXPIRE_HOURS * 3600
    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": iat,
        "exp": exp,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """Raises jwt.ExpiredSignatureError / jwt.InvalidTokenError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
