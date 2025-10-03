from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "person"  # 'person', 'company_admin', 'company_member'
    company_name: str = None  # Only for company_admin registration

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

class UserRole(BaseModel):
    role: str

class CompanyCreate(BaseModel):
    name: str

class CompanyContactCreate(BaseModel):
    email: EmailStr = None
    telegram_user_id: str = None

class CompanyContactResponse(BaseModel):
    id: int
    email: EmailStr = None
    telegram_user_id: str = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    contacts: list[CompanyContactResponse] = []
