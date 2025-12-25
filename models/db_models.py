from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    contacts = relationship("CompanyContact", back_populates="company")
    users = relationship("User", back_populates="company")

class CompanyContact(Base):
    __tablename__ = "company_contacts"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    email = Column(String, nullable=True)
    telegram_user_id = Column(String, nullable=True)
    company = relationship("Company", back_populates="contacts")

    event_date = Column(DateTime)
    event_time = Column(String)
    source_file = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
