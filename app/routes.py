from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Store
from app.security import verify_pin, create_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# =========================
# LOGIN
# =========================
@router.post("/login")
def login(
    request: Request,
    store_id: int = Form(...),
    pin: str = Form(...)
):
    db: Session = SessionLocal()

    store = db.query(Store).filter(Store.store_id == store_id, Store.active == True).first()
    db.close()

    if not store:
        return RedirectResponse(url="/?error=store_not_found", status_code=302)

    if not verify_pin(pin, store.pin_hash):
        return RedirectResponse(url="/?error=invalid_pin", status_code=302)

    token = create_token(store.store_id, store.name)

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="brasa_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return response

# =========================
# DASHBOARD (PROTEGIDO)
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    token = request.cookies.get("brasa_token")

    if not token:
        return RedirectResponse(url="/?error=unauthorized", status_code=302)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )
