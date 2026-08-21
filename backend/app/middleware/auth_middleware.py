from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


async def auth_middleware(request: Request, call_next):
    """
    JWT Authentication Middleware
    """

    public_routes = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",

        # Authentication Routes
        "/api/v1/auth/login",
        "/api/v1/auth/register",

        # Swagger static files
        "/docs/oauth2-redirect",
        "/favicon.ico",
    ]

    path = request.url.path

    # Allow all public routes
    if path in public_routes:
        return await call_next(request)

    # Allow Swagger assets
    if path.startswith("/docs"):
        return await call_next(request)

    # Get Authorization Header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization token missing"}
        )

    try:
        scheme, token = auth_header.split()

        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        request.state.user = payload

    except (JWTError, ValueError):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"}
        )

    response = await call_next(request)
    return response