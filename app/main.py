from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router

# IMPORT DO SEED (PASSO 4.2)
from app.seed import run as seed_run

app = FastAPI(title="BRASA Meat Intelligence™", version="1.0.0")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    # Inicializa o banco e cria tabelas
    init_db()

    # SEED AUTOMÁTICO DA LOJA PILOTO (REMOVE DEPOIS)
    seed_run()

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

# Registra todas as rotas da aplicação
app.include_router(router)
