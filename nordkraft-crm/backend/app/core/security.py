from datetime import datetime, timedelta
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, role: str, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode: dict[str, Any] = {"exp": expire, "sub": subject, "role": role}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

