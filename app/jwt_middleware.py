from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from typing import Callable, List
from .auth import decode_token
import jwt

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Enforces Authorization: Bearer <access_token> on protected routes.
    Skips auth for configured public paths (health, auth, docs).
    Accepts only tokens with claim type == 'access'.
    """
    def __init__(self, app: ASGIApp, public_paths: List[str] | None = None):
        super().__init__(app)
        self.public_paths = set(public_paths or [])

    async def dispatch(self, request, call_next: Callable):
        path = request.url.path

        # Allow public endpoints
        if (
            path in self.public_paths or
            path.startswith("/auth/") or
            path in ("/openapi.json", "/docs", "/redoc")
        ):
            return await call_next(request)

        # Expect Authorization header
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth or not auth.lower().startswith("bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth.split(" ", 1)[1].strip()
        try:
            claims = decode_token(token)
            if claims.get("type") != "access":
                return JSONResponse({"detail": "Invalid token type"}, status_code=401)
            # Attach identity for handlers if needed
            request.state.user = claims.get("sub")
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        return await call_next(request)
