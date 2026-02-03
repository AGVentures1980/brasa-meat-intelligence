from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

from app.database import SessionLocal
from app.models import Store, UploadBatch, OrderLine, ItemMap
from app.security import verify_pin, create_token, decode_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_store(request: Request, db: Session) -> Store | None:
    token = request.cookies.get("brasa_token")
    if not token:
        return None
    data = decode_token(token)
    store_id = data.get("store_db_id")
    if not store_id:
        return None
    return db.query(Store).filter(Store.id == store_id, Store.active == True).first()

@router.get("/health")
def health():
    return {"system": "BRASA Meat Intelligence™", "status": "ONLINE"}

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    pin: str = Form(...),
    db: Session = Depends(get_db),
):
    store = db.query(Store).filter(Store.email == email, Store.active == True).first()
    if not store or not verify_pin(pin, store.pin_hash):
        # volta para login com erro
        url = "/?error=Credenciais inválidas"
        return RedirectResponse(url, status_code=302)

    token = create_token({"store_db_id": store.id, "store_id": store.store_id})
    resp = RedirectResponse("/app", status_code=302)
    resp.set_cookie("brasa_token", token, httponly=True, samesite="lax")
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("brasa_token")
    return resp

@router.get("/app", response_class=HTMLResponse)
def app_page(request: Request, db: Session = Depends(get_db)):
    store = get_current_store(request, db)
    if not store:
        return RedirectResponse("/", status_code=302)
    # app.html pode ser seu painel premium
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("app.html", {"request": request, "store": store})

def normalize_item(db: Session, raw_item: str):
    """
    Busca mapeamento do item. Se não existir, cria como "needs_review".
    """
    m = db.query(ItemMap).filter(ItemMap.raw_item == raw_item, ItemMap.active == True).first()
    if not m:
        m = ItemMap(raw_item=raw_item, protein=None, weight_lb=None, combo_proteins=None)
        db.add(m)
        db.commit()
        db.refresh(m)
    return m

@router.post("/api/upload/olo")
def upload_olo_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    store = get_current_store(request, db)
    if not store:
        return {"ok": False, "error": "unauthorized"}

    content = file.file.read()
    df = pd.read_csv(pd.io.common.BytesIO(content))

    # Ajuste esses nomes quando você mandar o print do CSV real:
    # esperados: item_name, quantity, order_id, order_dt
    # se vier diferente, a gente adapta aqui.
    required_cols = ["item_name", "quantity"]
    for c in required_cols:
        if c not in df.columns:
            return {"ok": False, "error": f"CSV sem coluna obrigatória: {c}", "columns": list(df.columns)}

    batch = UploadBatch(store_id=store.id, original_filename=file.filename, status="processed")
    db.add(batch)
    db.commit()
    db.refresh(batch)

    created = 0
    needs_review = 0

    for _, row in df.iterrows():
        raw_item = str(row["item_name"]).strip()
        qty = int(row["quantity"]) if str(row["quantity"]).strip() else 1

        m = normalize_item(db, raw_item)

        protein = m.protein
        weight_lb = m.weight_lb

        if protein is None or weight_lb is None:
            needs_review += 1
            batch.status = "needs_review"

        ol = OrderLine(
            store_id=store.id,
            upload_batch_id=batch.id,
            order_id=str(row["order_id"]) if "order_id" in df.columns else None,
            raw_item=raw_item,
            quantity=qty,
            protein=protein,
            weight_lb=weight_lb,
            notes=None
        )
        db.add(ol)
        created += 1

    db.commit()
    db.refresh(batch)

    return {"ok": True, "batch_id": batch.id, "lines_created": created, "needs_review": needs_review, "batch_status": batch.status}
