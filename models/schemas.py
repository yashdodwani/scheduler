from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Pydantic v2: enable ORM serialization for response models
try:
    from pydantic import ConfigDict  # type: ignore
except Exception:  # fallback for older Pydantic
    ConfigDict = None  # type: ignore


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "person"  # 'person', 'company_admin', 'company_member'
    company_name: str | None = None  # Only for company_admin registration


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
    # Enable ORM mode / from_attributes for SQLAlchemy models
    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:
        class Config:
            orm_mode = True


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
    email: EmailStr | None = None
    telegram_user_id: str | None = None


class CompanyContactResponse(BaseModel):
    id: int
    email: EmailStr | None = None
    telegram_user_id: str | None = None
    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:
        class Config:
            orm_mode = True


class CompanyResponse(BaseModel):
    id: int
    name: str
    contacts: list[CompanyContactResponse] = Field(default_factory=list)
    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:
        class Config:
            orm_mode = True
