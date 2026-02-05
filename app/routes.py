import csv
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models import OrderItem, Recipe
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =========================
# DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# DASHBOARD
# =========================

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# =========================
# UPLOAD CSV
# =========================

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload-orders")
def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    contents = file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(contents)

    inserted = 0

    for row in reader:
        record = OrderItem(
            store_id=int(row["store_id"]),
            item_name=row["item_name"],
            qty=float(row["qty"]),
            order_date=row["order_date"]
        )
        db.add(record)
        inserted += 1

    db.commit()

    return {"status": "ok", "rows_inserted": inserted}


# =========================
# CONSUMO
# =========================

@router.get("/consumption/{store_id}", response_class=HTMLResponse)
def consumption(store_id: int, request: Request, db: Session = Depends(get_db)):

    results = (
        db.query(
            Recipe.cut,
            func.sum(OrderItem.qty * Recipe.qty_per_unit)
        )
        .join(
            Recipe,
            (Recipe.item_name == OrderItem.item_name) &
            (Recipe.store_id == OrderItem.store_id)
        )
        .filter(OrderItem.store_id == store_id)
        .group_by(Recipe.cut)
        .all()
    )

    data = [{"cut": r[0], "total": float(r[1])} for r in results]

    return templates.TemplateResponse(
        "consumption.html",
        {"request": request, "data": data}
    )
