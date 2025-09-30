# routers/events.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List
from models.db_models import Event, User
from models.schemas import EventResponse
from services.utils import get_current_user, get_database

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[EventResponse])
async def get_events(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    events = db.query(Event).filter(Event.user_id == current_user.id).order_by(Event.event_date).all()
    return events

@router.get("/today", response_model=List[EventResponse])
async def get_today_events(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    today = date.today()
    events = db.query(Event).filter(
        Event.user_id == current_user.id,
        Event.event_date >= datetime.combine(today, datetime.min.time()),
        Event.event_date < datetime.combine(today + timedelta(days=1), datetime.min.time())
    ).order_by(Event.event_date).all()
    return events

@router.delete("/{event_id}")
async def delete_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

