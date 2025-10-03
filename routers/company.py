from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.db_models import User, CompanyContact
from models.schemas import CompanyContactCreate, CompanyContactResponse
from services.utils import get_current_user, get_database
from typing import List

router = APIRouter(prefix="/company", tags=["company"])

@router.get("/contacts", response_model=List[CompanyContactResponse])
async def list_company_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    if current_user.role != "company_admin" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Only company admins can view company contacts.")
    contacts = db.query(CompanyContact).filter(CompanyContact.company_id == current_user.company_id).all()
    return contacts

@router.post("/contacts", response_model=CompanyContactResponse)
async def add_company_contact(contact: CompanyContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    if current_user.role != "company_admin" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Only company admins can add company contacts.")
    if not contact.email and not contact.telegram_user_id:
        raise HTTPException(status_code=400, detail="At least one of email or telegram_user_id must be provided.")
    new_contact = CompanyContact(
        company_id=current_user.company_id,
        email=contact.email,
        telegram_user_id=contact.telegram_user_id
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.delete("/contacts/{contact_id}")
async def delete_company_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    if current_user.role != "company_admin" or not current_user.company_id:
        raise HTTPException(status_code=403, detail="Only company admins can delete company contacts.")
    contact = db.query(CompanyContact).filter(CompanyContact.id == contact_id, CompanyContact.company_id == current_user.company_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully."}

