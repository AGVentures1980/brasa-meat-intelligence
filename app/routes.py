from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import csv
import io

from app.database import SessionLocal
from app.models import MeatUsage, Order
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ==========================
# DB SESSION
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================
# DASHBOARD
# ==========================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

# ==========================
# UPLOAD CSV PAGE
# ==========================
@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

# ==========================
# PROCESS CSV
# ==========================
@router.post("/upload-orders")
def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(content))

    inserted = 0

    for row in csv_reader:
        record = Order(
            store_id=int(row["store_id"]),
            order_id=row["order_id"],
            item=row["item"],
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

# ==========================
# CONSUMPTION VIEW
# ==========================
@router.get("/consumption/{store_id}", response_class=HTMLResponse)
def consumption_view(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    records = db.query(Order).filter(
        Order.store_id == store_id
    ).all()

    total_orders = len(records)

    total_qty = sum(r.qty for r in records)

    return templates.TemplateResponse(
        "consumption.html",
        {
            "request": request,
            "store_id": store_id,
            "total_orders": total_orders,
            "total_qty": total_qty
        }
    )
