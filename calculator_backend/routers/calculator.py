from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from calculator_backend import database, models, schemas
from calculator_backend.utils.jwt_handler import verify_token
from calculator_backend.database import get_db
router = APIRouter(prefix="/calc", tags=["Calculator"])

@router.post("/calculate")
def calculate(expr: schemas.Expression, Authorization: str = Header(None), db: Session = Depends(get_db)):
    token = Authorization.split(" ")[1] if Authorization else None
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = str(eval(expr.expr, {"__builtins__": None}, {}))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid expression")

    user = db.query(models.User).filter(models.User.username == username).first()
    history = models.History(user_id=user.id, expression=expr.expr, result=result)
    db.add(history)
    db.commit()
    return {"expression": expr.expr, "result": result}

@router.get("/history")
def get_history(Authorization: str = Header(None), db: Session = Depends(get_db)):
    token = Authorization.split(" ")[1] if Authorization else None
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.username == username).first()
    records = db.query(models.History).filter(models.History.user_id == user.id).all()
    return records
