# services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, date
import pytz
from config import TIMEZONE
from models.db_models import User, Event
from services.email_service import send_email
from services.telegram_service import send_telegram_message
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URL
from sqlalchemy.orm import sessionmaker

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        send_daily_notifications,
        CronTrigger(hour=8, minute=0, timezone=pytz.timezone(TIMEZONE))
    )
    scheduler.start()

async def send_daily_notifications():
    db = SessionLocal()
    try:
        today = date.today()
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            today_events = db.query(Event).filter(
                Event.user_id == user.id,
                Event.event_date >= datetime.combine(today, datetime.min.time()),
                Event.event_date < datetime.combine(today + timedelta(days=1), datetime.min.time())
            ).all()
            if today_events:
                email_body = f"""
                <html><head></head><body><h2>Today's Schedule - {today.strftime('%B %d, %Y')}</h2><p>Here are your events for today:</p><ul>
                """
                telegram_message = f"📅 <b>Today's Schedule - {today.strftime('%B %d, %Y')}</b>\n\n"
                for event in today_events:
                    email_body += f"<li><strong>{event.title}</strong> at {event.event_time}<br><em>{event.description}</em></li>"
                    telegram_message += f"🕒 <b>{event.title}</b> at {event.event_time}\n{event.description}\n\n"
                email_body += "</ul><p>Have a great day!</p><p><em>Schedule Management App</em></p></body></html>"
                await send_email(user.email, f"Today's Schedule - {today.strftime('%B %d, %Y')}", email_body)
                if user.telegram_user_id:
                    await send_telegram_message(user.telegram_user_id, telegram_message)
    finally:
        db.close()

