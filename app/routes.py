from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MeatUsage, Order
import csv
import io
from datetime import datetime

router = APIRouter()

# DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
# MEAT USAGE
# ===============================
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

# ===============================
# CSV UPLOAD — ORDERS
# ===============================
@router.post("/upload-orders")
def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(content))

    inserted = 0

    for row in csv_reader:
        order = Order(
            store_id=int(row["store_id"]),
            order_id=row["order_id"],
            item_name=row["item_name"],
            qty=float(row["qty"]),
            order_date=datetime.fromisoformat(row["order_date"])
        )
        db.add(order)
        inserted += 1

    db.commit()

    return {
        "status": "uploaded",
        "rows_inserted": inserted
    }
