from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="JWT FastAPI Demo", version="1.0.0")

JWT_SECRET = "change-this-in-production-32-bytes"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300
REFRESH_TOKEN_EXPIRE_SECONDS = 3600
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


class LoginRequest(BaseModel):
    username: str | None = Field(default=None)
    user: str | None = Field(default=None)
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
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@app.post("/token", response_model=TokenResponse)
def create_token(credentials: LoginRequest) -> TokenResponse:
    username = credentials.username or credentials.user
    if username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
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
