# services/telegram_bot.py
from services.telegram_service import send_telegram_message
from models.db_models import User, Event
from services.utils import SessionLocal
import json
from datetime import datetime, timedelta

class ScheduleBotWebhook:
    def __init__(self):
        pass

    async def webhook_handler(self, body: str):
        try:
            data = json.loads(body)
            message = data.get("message")
            if not message:
                return {"ok": True}
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            # Simple command: /today
            if text.strip().lower() == "/today":
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.telegram_user_id == str(chat_id)).first()
                    if not user:
                        await send_telegram_message(str(chat_id), "You are not linked to any account. Please link your account in the web app.")
                        return {"ok": True}
                    today = datetime.now().date()
                    events = db.query(Event).filter(
                        Event.user_id == user.id,
                        Event.event_date >= datetime.combine(today, datetime.min.time()),
                        Event.event_date < datetime.combine(today + timedelta(days=1), datetime.min.time())
                    ).order_by(Event.event_date).all()
                    if not events:
                        await send_telegram_message(str(chat_id), "No events found for today.")
                    else:
                        msg = f"📅 <b>Today's Schedule - {today.strftime('%B %d, %Y')}</b>\n\n"
                        for event in events:
                            msg += f"🕒 <b>{event.title}</b> at {event.event_time}\n{event.description}\n\n"
                        await send_telegram_message(str(chat_id), msg)
                finally:
                    db.close()
            else:
                await send_telegram_message(str(chat_id), "Send /today to get today's events.")
            return {"ok": True}
        except Exception as e:
            print(f"Error in webhook_handler: {e}")
            return {"ok": False, "error": str(e)}

