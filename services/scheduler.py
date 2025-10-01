from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, date, time as dt_time
import pytz
from config import TIMEZONE
from models.db_models import User, Event
from services.email_service import send_email
from services.telegram_service import send_telegram_message
from services.utils import SessionLocal
import asyncio

scheduler = BackgroundScheduler()

# Helper to schedule notification jobs for each user
async def send_user_notifications(user, notify_date, db, is_one_day_before=False):
    # Get events for the notify_date
    events = db.query(Event).filter(
        Event.user_id == user.id,
        Event.event_date >= datetime.combine(notify_date, datetime.min.time()),
        Event.event_date < datetime.combine(notify_date + timedelta(days=1), datetime.min.time())
    ).all()
    if events:
        day_label = notify_date.strftime('%B %d, %Y')
        if is_one_day_before:
            email_subject = f"Tomorrow's Schedule - {day_label}"
            email_intro = f"<h2>Tomorrow's Schedule - {day_label}</h2><p>Here are your events for tomorrow:</p>"
            telegram_intro = f"📅 <b>Tomorrow's Schedule - {day_label}</b>\n\n"
        else:
            email_subject = f"Today's Schedule - {day_label}"
            email_intro = f"<h2>Today's Schedule - {day_label}</h2><p>Here are your events for today:</p>"
            telegram_intro = f"📅 <b>Today's Schedule - {day_label}</b>\n\n"
        email_body = f"<html><head></head><body>{email_intro}<ul>"
        telegram_message = telegram_intro
        for event in events:
            email_body += f"<li><strong>{event.title}</strong> at {event.event_time}<br><em>{event.description}</em></li>"
            telegram_message += f"🕒 <b>{event.title}</b> at {event.event_time}\n{event.description}\n\n"
        email_body += "</ul><p>Have a great day!</p><p><em>Schedule Management App</em></p></body></html>"
        await send_email(user.email, email_subject, email_body)
        if user.telegram_user_id:
            await send_telegram_message(user.telegram_user_id, telegram_message)

async def notification_dispatcher():
    db = SessionLocal()
    try:
        now = datetime.now(pytz.timezone(TIMEZONE))
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            # Parse user's notification_time
            try:
                user_hour, user_minute = map(int, user.notification_time.split(":"))
            except Exception:
                user_hour, user_minute = 8, 0  # fallback
            # If current time matches user's notification time, send today's events
            if now.hour == user_hour and now.minute == user_minute:
                await send_user_notifications(user, now.date(), db, is_one_day_before=False)
            # If user wants one day before notification, check for that too
            if user.notify_one_day_before:
                # Send notification for tomorrow's events at user's notification time
                tomorrow = now.date() + timedelta(days=1)
                if now.hour == user_hour and now.minute == user_minute:
                    await send_user_notifications(user, tomorrow, db, is_one_day_before=True)
    finally:
        db.close()

def start_scheduler():
    # Run notification_dispatcher every minute
    scheduler.add_job(
        lambda: asyncio.run(notification_dispatcher()),
        CronTrigger(minute="*", timezone=pytz.timezone(TIMEZONE))
    )
    scheduler.start()
