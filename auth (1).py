from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import User
from app.schemas import TokenResponse
from app.service.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user_by_email,
    get_user_by_username,
    hash_password,
)


router = APIRouter(
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    auto_error=False,
)


def get_current_user_from_request(
    request: Request,
    db: Session,
) -> User | None:

    token = request.cookies.get(
        "access_token"
    )

    if not token:
        auth_header = request.headers.get(
            "Authorization",
            "",
        )

        if auth_header.lower().startswith(
            "bearer "
        ):
            token = auth_header.split(
                " ",
                1,
            )[1]

    if not token:
        return None

    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except ValueError:
        return None

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_current_active_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:

    user = get_current_user_from_request(
        request,
        db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return user


@router.post(
    "/register",
    name="register_user",
)
def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters.",
        )

    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters.",
        )

    if get_user_by_username(
        db,
        username,
    ):
        raise HTTPException(
            status_code=400,
            detail="Username already exists.",
        )

    if get_user_by_email(
        db,
        email,
    ):
        raise HTTPException(
            status_code=400,
            detail="Email already exists.",
        )

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(
            password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RedirectResponse(
        url="/login?registered=1",
        status_code=303,
    )


@router.post(
    "/login",
    name="login_user",
)
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db,
        username.strip(),
        password,
    )

    if not user:
        return RedirectResponse(
            url="/login?error=invalid",
            status_code=303,
        )

    token = create_access_token(
        user.id,
        user.username,
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=3600,
    )

    return response


@router.get(
    "/logout",
    name="logout",
)
def logout():

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie(
        "access_token"
    )

    return response


@router.post(
    "/token",
    response_model=TokenResponse,
)
def token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db,
        username,
        password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
        )

    access_token = create_access_token(
        user.id,
        user.username,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )