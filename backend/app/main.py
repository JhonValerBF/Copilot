from datetime import datetime, timedelta, timezone
import os
import secrets
from typing import Literal
from uuid import uuid4

import jwt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="JWT FastAPI Demo", version="1.0.0")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300
REFRESH_TOKEN_EXPIRE_SECONDS = 3600
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

missing_vars = [
    name
    for name, value in (
        ("JWT_SECRET", JWT_SECRET),
        ("ADMIN_USERNAME", ADMIN_USERNAME),
        ("ADMIN_PASSWORD", ADMIN_PASSWORD),
    )
    if not value
]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS
    refresh_token: str


def _create_token(subject: str, token_type: str, expires_in: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@app.post("/token", response_model=TokenResponse)
def create_token(credentials: LoginRequest) -> TokenResponse:
    valid_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    valid_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=_create_token(ADMIN_USERNAME, "access", ACCESS_TOKEN_EXPIRE_SECONDS),
        refresh_token=_create_token(ADMIN_USERNAME, "refresh", REFRESH_TOKEN_EXPIRE_SECONDS),
    )


@app.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest) -> TokenResponse:
    try:
        data = jwt.decode(
            payload.refresh_token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    subject = data.get("sub")
    if subject != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    return TokenResponse(
        access_token=_create_token(subject, "access", ACCESS_TOKEN_EXPIRE_SECONDS),
        refresh_token=_create_token(subject, "refresh", REFRESH_TOKEN_EXPIRE_SECONDS),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
