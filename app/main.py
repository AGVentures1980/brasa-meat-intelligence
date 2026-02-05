from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router
from app.seed import seed_store, seed_recipes

app = FastAPI(
    title="BRASA Meat Intelligence™",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


# ==============================
# STARTUP BLOCK — COPIA INTEIRO
# ==============================

@app.on_event("startup")
def startup():

    print("======================================")
    print("BRASA STARTUP: Inicializando sistema…")
    print("======================================")

    # 1️⃣ Criar tabelas
    print("BRASA STARTUP: Inicializando banco…")
    init_db()

    # 2️⃣ Seed loja piloto (Texas)
    print("BRASA STARTUP: Seed loja piloto…")
    try:
        seed_store()
        print("BRASA STARTUP: Loja piloto OK")
    except Exception as e:
        print("BRASA STARTUP: Loja já existe — SKIPPED")
        print("Detalhe:", e)

    # 3️⃣ Seed receitas padrão
    print("BRASA STARTUP: Seed receitas…")
    try:
        seed_recipes()
        print("BRASA STARTUP: Receitas OK")
    except Exception as e:
        print("BRASA STARTUP: Receitas já existem — SKIPPED")
        print("Detalhe:", e)

    print("======================================")
    print("BRASA STARTUP: Sistema pronto 🚀")
    print("======================================")


# ==============================
# LOGIN PAGE
# ==============================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ==============================
# ROUTES
# ==============================

app.include_router(router)
