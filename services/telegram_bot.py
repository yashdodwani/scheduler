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
            text = message.get("text", "").strip().lower()

            db = SessionLocal()
            try:
                # /start command
                if text == "/start":
                    welcome = (
                        "👋 <b>Welcome to ScheduleBot!</b>\n\n"
                        "Use /connect to get your Telegram User ID and link it with your web app account.\n"
                        "Use /help to see all available commands."
                    )
                    await send_telegram_message(str(chat_id), welcome)
                # /help command
                elif text == "/help":
                    help_msg = (
                        "<b>ScheduleBot Help</b>\n\n"
                        "/start - Welcome message and setup guide\n"
                        "/help - Show this help information\n"
                        "/connect - Get your Telegram User ID for linking\n"
                        "/today - Show today's scheduled events\n"
                        "/events - Show all upcoming events\n"
                    )
                    await send_telegram_message(str(chat_id), help_msg)
                # /connect command
                elif text == "/connect":
                    connect_msg = (
                        f"<b>Your Telegram User ID:</b> <code>{chat_id}</code>\n"
                        "Copy this ID and link it in your web app profile to receive notifications."
                    )
                    await send_telegram_message(str(chat_id), connect_msg)
                # /today command
                elif text == "/today":
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
                # /events command
                elif text == "/events":
                    user = db.query(User).filter(User.telegram_user_id == str(chat_id)).first()
                    if not user:
                        await send_telegram_message(str(chat_id), "You are not linked to any account. Please link your account in the web app.")
                        return {"ok": True}
                    now = datetime.now()
                    events = db.query(Event).filter(
                        Event.user_id == user.id,
                        Event.event_date >= now
                    ).order_by(Event.event_date).all()
                    if not events:
                        await send_telegram_message(str(chat_id), "No upcoming events found.")
                    else:
                        msg = f"📅 <b>Upcoming Events</b>\n\n"
                        for event in events:
                            msg += f"🗓️ <b>{event.title}</b> on {event.event_date.strftime('%Y-%m-%d')} at {event.event_time}\n{event.description}\n\n"
                        await send_telegram_message(str(chat_id), msg)
                # Inline keyboard example for /help
                elif text == "buttons":
                    # Example: send inline keyboard
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "Today's Events", "callback_data": "today"},
                                {"text": "Upcoming Events", "callback_data": "events"}
                            ],
                            [
                                {"text": "Help", "callback_data": "help"}
                            ]
                        ]
                    }
                    payload = {
                        "chat_id": chat_id,
                        "text": "Choose an option:",
                        "reply_markup": keyboard,
                        "parse_mode": "HTML"
                    }
                    import requests
                    from config import TELEGRAM_API_URL
                    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
                else:
                    await send_telegram_message(str(chat_id), "Send /help to see available commands.")
            finally:
                db.close()
            return {"ok": True}
        except Exception as e:
            print(f"Error in webhook_handler: {e}")
            return {"ok": False, "error": str(e)}
