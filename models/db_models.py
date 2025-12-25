from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("CompanyContact", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Roles / company support (added by alembic migration 4da1c2f0cb74)
    role = Column(String, default="person")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    # Notification settings
    notification_time = Column(String, default="08:00")  # HH:MM
    notify_one_day_before = Column(Boolean, default=False)

    # Messaging
    telegram_user_id = Column(String, nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="users")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")


class CompanyContact(Base):
    __tablename__ = "company_contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String, nullable=True)
    telegram_user_id = Column(String, nullable=True)

    company = relationship("Company", back_populates="contacts")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, default="")
    event_date = Column(DateTime, nullable=False)
    event_time = Column(String, nullable=False)
    source_file = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="events")
