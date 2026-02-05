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
# STARTUP
# ==============================
@app.on_event("startup")
def startup():

    print("======================================")
    print("BRASA STARTUP: Inicializando sistema")
    print("======================================")

    init_db()

    try:
        seed_store()
        print("Seed loja OK")
    except Exception:
        print("Seed loja SKIPPED")

    try:
        seed_recipes()
        print("Seed receitas OK")
    except Exception:
        print("Seed receitas SKIPPED")

    print("======================================")
    print("BRASA STARTUP: Sistema pronto 🚀")
    print("======================================")

# ==============================
# LOGIN
# ==============================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

# ==============================
# ROUTES (CRÍTICO)
# ==============================
app.include_router(router)
