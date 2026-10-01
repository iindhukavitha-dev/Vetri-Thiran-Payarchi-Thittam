import json

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import RecommendationHistory
from app.router.auth import get_current_active_user
from app.service.gemini_utils import (
    generate_home_recommendations,
    generate_jewelry_recommendations,
    generate_party_recommendations,
)


router = APIRouter(
    tags=["Planners"]
)


def _save_history(
    db: Session,
    user_id: int,
    planner_type: str,
    request_data: dict,
    response_data: dict,
):
    record = RecommendationHistory(
        user_id=user_id,
        planner_type=planner_type,
        request_json=json.dumps(
            request_data,
            default=str,
        ),
        response_json=json.dumps(
            response_data,
            default=str,
        ),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.post(
    "/generate-home",
)
def generate_home(
    request: Request,
    budget: float = Form(...),
    rooms: list[str] = Form(...),
    style: str = Form("Modern"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):

    result = generate_home_recommendations(
        budget=budget,
        rooms=rooms,
        style=style,
        notes=notes,
    )

    record = _save_history(
        db=db,
        user_id=current_user.id,
        planner_type="home",
        request_data={
            "budget": budget,
            "rooms": rooms,
            "style": style,
            "notes": notes,
        },
        response_data=result,
    )

    return RedirectResponse(
        url=f"/recommendations/{record.id}",
        status_code=303,
    )


@router.post(
    "/generate-party",
)
def generate_party(
    request: Request,
    budget: float = Form(...),
    guests: int = Form(...),
    event_type: str = Form("Birthday"),
    venue: str = Form(""),
    preferences: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):

    result = generate_party_recommendations(
        budget=budget,
        guests=guests,
        event_type=event_type,
        venue=venue,
        preferences=preferences,
    )

    record = _save_history(
        db=db,
        user_id=current_user.id,
        planner_type="party",
        request_data={
            "budget": budget,
            "guests": guests,
            "event_type": event_type,
            "venue": venue,
            "preferences": preferences,
        },
        response_data=result,
    )

    return RedirectResponse(
        url=f"/recommendations/{record.id}",
        status_code=303,
    )


@router.post(
    "/generate-jewelry",
)
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form("Wedding"),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):

    image_bytes = None
    mime_type = None

    if outfit_image and outfit_image.filename:
        image_bytes = await outfit_image.read()
        mime_type = outfit_image.content_type

        if len(image_bytes) > 5 * 1024 * 1024:
            return RedirectResponse(
                url="/jewelry-planner?error=image-too-large",
                status_code=303,
            )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if mime_type not in allowed_types:
            return RedirectResponse(
                url="/jewelry-planner?error=invalid-image",
                status_code=303,
            )

    result = generate_jewelry_recommendations(
        budget=budget,
        occasion=occasion,
        outfit_description=outfit_description,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    record = _save_history(
        db=db,
        user_id=current_user.id,
        planner_type="jewelry",
        request_data={
            "budget": budget,
            "occasion": occasion,
            "outfit_description": outfit_description,
            "image_provided": image_bytes is not None,
        },
        response_data=result,
    )

    return RedirectResponse(
        url=f"/recommendations/{record.id}",
        status_code=303,
    )