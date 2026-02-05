from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import csv
from datetime import datetime

from app.database import SessionLocal
from app.models import Order, Recipe

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-orders")
def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(content)

    inserted = 0

    for row in reader:
        order = Order(
            store_id=int(row["store_id"]),
            order_id=row["order_id"],
            item_name=row["item_name"],
            qty=float(row["qty"]),
            order_date=datetime.strptime(row["order_date"], "%Y-%m-%d").date()
        )
        db.add(order)
        inserted += 1

    db.commit()

    return {
        "status": "ok",
        "rows_inserted": inserted
    }

@router.get("/meat-consumption/{store_id}")
def meat_consumption(store_id: int, db: Session = Depends(get_db)):
    results = {}

    orders = db.query(Order).filter_by(store_id=store_id).all()

    for order in orders:
        recipe = db.query(Recipe).filter_by(item_name=order.item_name).first()
        if not recipe:
            continue

        consumed = order.qty * recipe.qty_lb

        if recipe.cut not in results:
            results[recipe.cut] = 0

        results[recipe.cut] += consumed

    return {
        "store_id": store_id,
        "consumption_lb": results
    }
