from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import TextIOWrapper

from app.database import SessionLocal
from app.models import OrderItem  # ajuste se o nome for outro

router = APIRouter()

# Dependency DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-orders")
def upload_orders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload de pedidos via CSV
    Esperado:
    store_id,order_id,item_name,qty,order_date
    """

    reader = csv.DictReader(
        TextIOWrapper(file.file, encoding="utf-8")
    )

    inserted = 0

    for row in reader:
        record = OrderItem(
            store_id=int(row["store_id"]),
            order_id=row["order_id"],
            item_name=row["item_name"],
            qty=float(row["qty"]),
            order_date=row["order_date"]
        )
        db.add(record)
        inserted += 1

    db.commit()

    return {
        "status": "ok",
        "rows_inserted": inserted
    }
