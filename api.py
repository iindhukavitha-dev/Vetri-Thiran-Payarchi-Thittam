import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import RecommendationHistory
from app.router.auth import get_current_active_user
from app.schemas import RecommendationResponse, SessionInfo
from app.service.auth import create_access_token
from app.service.gemini_utils import (
    generate_home_recommendations,
    generate_jewelry_recommendations,
    generate_party_recommendations,
)


router = APIRouter(
    prefix="/api",
    tags=["API"],
)


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "PocketSmart AI",
    }


@router.post(
    "/home",
    response_model=RecommendationResponse,
)
def home_api(
    budget: float = Form(...),
    rooms: list[str] = Form(...),
    style: str = Form("Modern"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):

    result = generate_home_recommendations(
        budget,
        rooms,
        style,
        notes,
    )

    record = RecommendationHistory(
        user_id=current_user.id,
        planner_type="home",
        request_json=json.dumps(
            {
                "budget": budget,
                "rooms": rooms,
                "style": style,
                "notes": notes,
            }
        ),
        response_json=json.dumps(result),
    )

    db.add(record)
    db.commit()

    return result


@router.post(
    "/party",
    response_model=RecommendationResponse,
)
def party_api(
    budget: float = Form(...),
    guests: int = Form(...),
    event_type: str = Form("Birthday"),
    venue: str = Form(""),
    preferences: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):

    result = generate_party_recommendations(
        budget,
        guests,
        event_type,
        venue,
        preferences,
    )

    record = RecommendationHistory(
        user_id=current_user.id,
        planner_type="party",
        request_json=json.dumps(
            {
                "budget": budget,
                "guests": guests,
                "event_type": event_type,
                "venue": venue,
                "preferences": preferences,
            }
        ),
        response_json=json.dumps(result),
    )

    db.add(record)
    db.commit()

    return result


@router.post(
    "/jewelry",
    response_model=RecommendationResponse,
)
async def jewelry_api(
    budget: float = Form(...),
    occasion: str = Form("Wedding"),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    current_user=Depends(get_current_active_user),
):

    image_bytes = None
    mime_type = None

    if outfit_image and outfit_image.filename:
        image_bytes = await outfit_image.read()
        mime_type = outfit_image.content_type

    return generate_jewelry_recommendations(
        budget=budget,
        occasion=occasion,
        outfit_description=outfit_description,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )


@router.get(
    "/session-info",
    response_model=SessionInfo,
)
def session_info(
    current_user=Depends(get_current_active_user),
):

    return SessionInfo(
        authenticated=True,
        user_id=current_user.id,
        username=current_user.username,
    )


@router.get(
    "/session-data",
)
def session_data(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    count = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == current_user.id
        )
        .count()
    )

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        },
        "recommendation_count": count,
    }


@router.get(
    "/history",
)
def history_api(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    records = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == current_user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": record.id,
            "planner_type": record.planner_type,
            "created_at": record.created_at.isoformat(),
            "response": json.loads(
                record.response_json
            ),
        }
        for record in records
    ]


@router.get(
    "/recommendations-details/{history_id}",
)
def recommendation_details_api(
    history_id: int,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):

    record = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.id == history_id,
            RecommendationHistory.user_id
            == current_user.id,
        )
        .first()
    )

    if not record:
        return {
            "error": "Recommendation not found."
        }

    return {
        "id": record.id,
        "planner_type": record.planner_type,
        "created_at": record.created_at.isoformat(),
        "request": json.loads(
            record.request_json
        ),
        "response": json.loads(
            record.response_json
        ),
    }