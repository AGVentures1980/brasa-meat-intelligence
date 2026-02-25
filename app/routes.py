from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import csv, io

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
# PROCESS CSV UPLOAD
# ==========================
@router.post("/upload-orders")
async def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    inserted = 0

    for row in reader:

        # 🔎 Detecta colunas automaticamente (tolerante a OLO / POS / Excel)
        item = (
            row.get("item")
            or row.get("product_name")
            or row.get("Menu Item")
            or row.get("menu_item")
            or row.get("Item")
        )

        qty = (
            row.get("qty")
            or row.get("quantity")
            or row.get("Qty")
            or row.get("Quantity")
            or 1
        )

        date = (
            row.get("order_date")
            or row.get("date")
            or row.get("Business Date")
            or row.get("Date")
        )

        store_id = (
            row.get("store_id")
            or 903   # default loja piloto
        )

        # Se não tiver item, ignora linha
        if not item:
            continue

        record = Order(
            store_id=int(store_id),
            item=item,
            qty=float(qty),
            order_date=date
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

