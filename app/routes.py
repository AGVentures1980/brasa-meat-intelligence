from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Store
from app.security import verify_pin

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    store_id: int = Form(...),
    pin: str = Form(...)
):
    db: Session = SessionLocal()

    try:
        store = db.query(Store).filter(Store.store_id == store_id).first()

        if not store:
            return request.app.state.templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Loja não encontrada"}
            )

        if not verify_pin(pin, store.pin_hash):
            return request.app.state.templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "PIN inválido"}
            )

        return HTMLResponse(
            f"""
            <h2>Login OK</h2>
            <p>Loja: {store.name}</p>
            <p>ID: {store.store_id}</p>
            """
        )

    finally:
        db.close()
