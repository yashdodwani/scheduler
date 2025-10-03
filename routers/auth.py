from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.db_models import User
from models.schemas import UserCreate, UserLogin, Token, TelegramUserID
from services.utils import hash_password, verify_password, create_access_token, get_current_user, get_database

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_database)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    if user.role == "company_admin":
        if not user.company_name:
            raise HTTPException(status_code=400, detail="Company name is required for company_admin registration")
        # Check if company already exists
        existing_company = db.query(models.db_models.Company).filter(models.db_models.Company.name == user.company_name).first()
        if existing_company:
            raise HTTPException(status_code=400, detail="Company name already registered")
        # Create company
        company = models.db_models.Company(name=user.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)
        db_user = User(email=user.email, hashed_password=hashed_password, role="company_admin", company_id=company.id)
    else:
        db_user = User(email=user.email, hashed_password=hashed_password, role="person")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_database)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/telegram")
async def set_telegram_user_id(telegram_data: TelegramUserID, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    current_user.telegram_user_id = telegram_data.telegram_user_id
    db.commit()
    return {"message": "Telegram user ID updated successfully"}
