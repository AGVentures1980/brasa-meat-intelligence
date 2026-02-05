from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MeatUsage

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/meat-usage")
def create_meat_usage(
    store_id: int = Form(...),
    cut: str = Form(...),
    received_qty: float = Form(...),
    used_qty: float = Form(...),
    waste_qty: float = Form(...),
    db: Session = Depends(get_db)
):
    record = MeatUsage(
        store_id=store_id,
        cut=cut,
        received_qty=received_qty,
        used_qty=used_qty,
        waste_qty=waste_qty
    )
    db.add(record)
    db.commit()
    return {"status": "ok"}
