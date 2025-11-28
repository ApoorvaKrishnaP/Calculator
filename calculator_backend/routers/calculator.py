from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from calculator_backend import models, schemas
from calculator_backend.utils.jwt_handler import verify_token
from calculator_backend.database import get_db
router = APIRouter(prefix="/calc", tags=["Calculator"])
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy import zoo, oo, nan
@router.post("/calculate")
def calculate(expr: schemas.Expression, Authorization: str = Header(None), db: Session = Depends(get_db)):
    token = Authorization.split(" ")[1] if Authorization else None
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        result = parse_expr(expr.expr).evalf()
        s = str(result).lower()
        if result is None or result == sp.nan or result == sp.zoo or 'zoo' in s or 'oo' in s or 'nan' in s:
            raise HTTPException(status_code=400, detail="Invalid Expression entered")
# alternatively also check is_finite if available:
        if getattr(result, "is_finite", None) is False:
            raise HTTPException(status_code=400, detail="Invalid Expression entered")
    except sp.SympifyError:
        raise HTTPException(status_code=400, detail="Invalid Expression entered")
    except ZeroDivisionError:
        # Handles division by zero specifically during evaluation
        raise HTTPException(status_code=400, detail="Cannot divide by zero")
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
print("I'm doing PR from vs code!")
print("I'm doing PR from vs code!")

