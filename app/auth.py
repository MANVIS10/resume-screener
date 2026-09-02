import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException

COOKIE_NAME = "admin_session"
MAX_AGE_SECONDS = 60 * 60 * 8  # 8 hours


def _serializer():
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY is not set")
    return URLSafeTimedSerializer(secret, salt="admin-auth")


def create_session_token() -> str:
    return _serializer().dumps({"admin": True})


def verify_session_token(token: str | None) -> bool:
    if not token:
        return False
    try:
        data = _serializer().loads(token, max_age=MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return False
    return bool(data.get("admin"))


def require_admin(request: Request) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if not verify_session_token(token):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
