from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.db_models import User
from models.schemas import UserNotificationSettings, UserNotificationSettingsResponse
from services.utils import get_current_user, get_database

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/notification-settings", response_model=UserNotificationSettingsResponse)
async def get_notification_settings(current_user: User = Depends(get_current_user)):
    return UserNotificationSettingsResponse(
        notification_time=current_user.notification_time,
        notify_one_day_before=current_user.notify_one_day_before
    )

@router.post("/notification-settings", response_model=UserNotificationSettingsResponse)
async def set_notification_settings(
    settings: UserNotificationSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    # Validate time format (HH:MM)
    try:
        hour, minute = map(int, settings.notification_time.split(":"))
        assert 0 <= hour < 24 and 0 <= minute < 60
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM (24-hour format)")
    current_user.notification_time = settings.notification_time
    current_user.notify_one_day_before = settings.notify_one_day_before
    db.commit()
    return UserNotificationSettingsResponse(
        notification_time=current_user.notification_time,
        notify_one_day_before=current_user.notify_one_day_before
    )

