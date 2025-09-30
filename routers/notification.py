# routers/notification.py
from fastapi import APIRouter, Depends
from services.email_service import send_email
from services.telegram_service import send_telegram_message
from services.utils import get_current_user

router = APIRouter(tags=["notification"])

@router.post("/test-notification")
async def test_notification(current_user = Depends(get_current_user)):
    await send_email(
        current_user.email,
        "Test Notification",
        "<h2>Test Email</h2><p>This is a test notification from Schedule Management App.</p>"
    )
    if current_user.telegram_user_id:
        await send_telegram_message(
            current_user.telegram_user_id,
            "🔔 <b>Test Notification</b>\n\nThis is a test notification from Schedule Management App."
        )
    return {"message": "Test notifications sent successfully"}

