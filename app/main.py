import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db, SessionLocal
from app.models import Store
from app.routes import router
from app.security import hash_pin

# =========================
# APP CONFIG
# =========================

app = FastAPI(
    title="BRASA Meat Intelligence™",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# =========================
# STARTUP — DB + AUTO SEED
# =========================

@app.on_event("startup")
def startup():
    print("BRASA STARTUP: Inicializando banco...")
    init_db()

    print("BRASA STARTUP: Verificando loja piloto...")
    db = SessionLocal()

    # =========================
    # LOJA PILOTO — TEXAS DE BRAZIL
    # =========================
    store_id = 903
    name = "Texas de Brazil - Tampa (Pilot)"
    email = "tampa@texasdebrazil.com"

    # PIN FINAL — TEM QUE SER IGUAL AO STRICT_STORE_PIN DO RENDER
    pin_plain = "TDB903"

    try:
        exists = db.query(Store).filter(Store.store_id == store_id).first()

        if not exists:
            s = Store(
                store_id=store_id,
                name=name,
                email=email,
                pin_hash=hash_pin(pin_plain),
                active=True
            )
            db.add(s)
            db.commit()
            print("SEED AUTO: Loja piloto criada com sucesso")
        else:
            print("SEED AUTO: Loja já existe — nenhuma ação necessária")

    except Exception as e:
        print("ERRO SEED AUTO:", str(e))

    finally:
        db.close()

# =========================
# ROTAS WEB
# =========================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": error
        }
    )

# =========================
# API ROUTES
# =========================

app.include_router(router)
