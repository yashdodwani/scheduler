from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TelegramUserID(BaseModel):
    telegram_user_id: str

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    event_time: str
    source_file: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserNotificationSettings(BaseModel):
    notification_time: str  # Format: HH:MM (24-hour)
    notify_one_day_before: bool

class UserNotificationSettingsResponse(BaseModel):
    notification_time: str
    notify_one_day_before: bool
