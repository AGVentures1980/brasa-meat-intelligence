import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router

# ======================================
# BRASA MEAT INTELLIGENCE — MAIN APP
# ======================================

app = FastAPI(
    title="BRASA Meat Intelligence™",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    print("BRASA STARTUP: Inicializando banco...")
    init_db()
    print("BRASA STARTUP: Banco OK")


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


# Rotas da API / Auth / Store
app.include_router(router)

# ======================================
# Healthcheck (Render / Monitoramento)
# ======================================

@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "service": "brasa-meat-intelligence",
        "env": os.getenv("RENDER_SERVICE_NAME", "local")
    }
