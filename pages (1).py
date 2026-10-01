import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import RecommendationHistory
from app.router.auth import get_current_user_from_request


templates = Jinja2Templates(
    directory="app/templates"
)

router = APIRouter()


def _user_or_redirect(
    request: Request,
    db: Session,
):
    user = get_current_user_from_request(
        request,
        db,
    )

    if not user:
        return None, RedirectResponse(
            "/login",
            status_code=303,
        )

    return user, None


@router.get("/")
def index(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user_from_request(
        request,
        db,
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/login")
def login_page(
    request: Request,
):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
        },
    )


@router.get("/register")
def register_page(
    request: Request,
):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
        },
    )


@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    history = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "history": history,
        },
    )


@router.get("/home-planner")
def home_planner(
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    return templates.TemplateResponse(
        "home_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/party-planner")
def party_planner(
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    return templates.TemplateResponse(
        "party_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/jewelry-planner")
def jewelry_planner(
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    return templates.TemplateResponse(
        "jewelry_planner.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/recommendations/{history_id}")
def recommendation_details(
    history_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    record = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.id == history_id,
            RecommendationHistory.user_id == user.id,
        )
        .first()
    )

    if not record:
        return RedirectResponse(
            "/history",
            status_code=303,
        )

    response = json.loads(
        record.response_json
    )

    return templates.TemplateResponse(
        "recommendations.html",
        {
            "request": request,
            "user": user,
            "record": record,
            "recommendation": response,
        },
    )


@router.get("/history")
def history_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user, redirect = _user_or_redirect(
        request,
        db,
    )

    if redirect:
        return redirect

    records = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "user": user,
            "records": records,
        },
    )
