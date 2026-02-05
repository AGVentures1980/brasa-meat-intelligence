raise Exception("ROUTES.PY CARREGADO")
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import csv
import io

from app.database import SessionLocal
from app.models import Order
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
# UPLOAD PAGE
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
async def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    inserted = 0

    for row in reader:
        order = Order(
            store_id=int(row["store_id"]),
            item=row["item"],
            qty=float(row["qty"]),
            order_date=row["order_date"]
        )
        db.add(order)
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
def consumption(
    request: Request,
    store_id: int,
    db: Session = Depends(get_db)
):

    orders = db.query(Order).filter(
        Order.store_id == store_id
    ).all()

    return templates.TemplateResponse(
        "consumption.html",
        {
            "request": request,
            "orders": orders,
            "store_id": store_id
        }
    )
