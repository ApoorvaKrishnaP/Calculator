from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from calculator_backend import models, schemas
from calculator_backend.utils.hashing import hash_password, verify_password
from calculator_backend.utils.jwt_handler import create_access_token
from calculator_backend.database import get_db
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
#Role of decorators,auth prefix
#In schemas.Usercreate,fastAPI validates user input
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = models.User(username=user.username, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
print("hey")
