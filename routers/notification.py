from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.db_models import CompanyContact
from services.email_service import send_email
from services.telegram_service import send_telegram_message
from services.utils import get_current_user, get_database

router = APIRouter(tags=["notification"])


@router.post("/test-notification")
async def test_notification(
    current_user=Depends(get_current_user), db: Session = Depends(get_database)
):
    if current_user.role == "company_admin" and current_user.company_id:
        contacts = (
            db.query(CompanyContact)
            .filter(CompanyContact.company_id == current_user.company_id)
            .all()
        )
        for contact in contacts:
            if contact.email:
                await send_email(
                    contact.email,
                    "Test Notification",
                    "<h2>Test Email</h2><p>This is a test notification from Schedule Management App.</p>",
                )
            if contact.telegram_user_id:
                await send_telegram_message(
                    contact.telegram_user_id,
                    "🔔 <b>Test Notification</b>\n\nThis is a test notification from Schedule Management App.",
                )
        # Also notify the admin themselves
        await send_email(
            current_user.email,
            "Test Notification",
            "<h2>Test Email</h2><p>This is a test notification from Schedule Management App.</p>",
        )
        if current_user.telegram_user_id:
            await send_telegram_message(
                current_user.telegram_user_id,
                "🔔 <b>Test Notification</b>\n\nThis is a test notification from Schedule Management App.",
            )
    else:
        await send_email(
            current_user.email,
            "Test Notification",
            "<h2>Test Email</h2><p>This is a test notification from Schedule Management App.</p>",
        )
        if current_user.telegram_user_id:
            await send_telegram_message(
                current_user.telegram_user_id,
                "🔔 <b>Test Notification</b>\n\nThis is a test notification from Schedule Management App.",
            )
    return {"message": "Test notifications sent successfully"}
