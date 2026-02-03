from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import router
from app.seed import run as seed_store

app = FastAPI(title="BRASA Meat Intelligence™", version="1.0.0")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    print("BRASA STARTUP: Inicializando banco...")
    init_db()

    print("BRASA STARTUP: Seed loja piloto...")
    try:
        seed_store()
        print("BRASA STARTUP: Seed OK")
    except Exception as e:
        print("BRASA STARTUP: Seed SKIPPED:", e)

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

app.include_router(router)
