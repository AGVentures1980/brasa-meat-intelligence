from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import MeatUsage

# Router principal
router = APIRouter()

# Templates
templates = Jinja2Templates(directory="templates")


# ---------------------------
# DB Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# PAGE — Formulário
# ---------------------------
@router.get("/meat-usage", response_class=HTMLResponse)
def meat_usage_page(request: Request):
    return templates.TemplateResponse(
        "meat_usage.html",
        {"request": request}
    )


# ---------------------------
# CREATE — Registro diário
# ---------------------------
@router.post("/meat-usage", response_class=HTMLResponse)
def create_meat_usage(
    request: Request,
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

    return templates.TemplateResponse(
        "meat_usage.html",
        {
            "request": request,
            "success": True
        }
    )
