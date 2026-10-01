from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db_models import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def get_user_by_username(
    db: Session,
    username: str,
) -> Optional[User]:
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> Optional[User]:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> Optional[User]:
    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


def create_access_token(
    user_id: int,
    username: str,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        return None