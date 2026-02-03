import os
import base64
import uuid
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

from openai import OpenAI

# ==============================
# CONFIG
# ==============================

APP_NAME = "BRASA Meat Intelligence™"

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
STRICT_STORE_PIN = os.getenv("STRICT_STORE_PIN", "true").lower() == "true"
STORE_PINS_RAW = os.getenv("STORE_PINS", "")

# ==============================
# FASTAPI
# ==============================

app = FastAPI(title=APP_NAME)

templates = Jinja2Templates(directory="templates")

# ==============================
# DATABASE
# ==============================

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class OrderRow(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String, index=True)
    order_id = Column(String, index=True)
    protein = Column(String)
    weight_lb = Column(Float)
    platform = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# ==============================
# SECURITY
# ==============================

STORE_PINS: Dict[str, str] = {}

if STORE_PINS_RAW:
    pairs = STORE_PINS_RAW.split(",")
    for p in pairs:
        if "=" in p:
            k, v = p.split("=")
            STORE_PINS[k.strip()] = v.strip()


def validate_store_pin(store_id: str, pin: str):
    if not STRICT_STORE_PIN:
        return True
    return STORE_PINS.get(store_id) == pin


# ==============================
# OPENAI CLIENT
# ==============================

client = OpenAI(api_key=OPENAI_API_KEY)


# ==============================
# UTILS
# ==============================

def image_to_base64(upload: UploadFile):
    return base64.b64encode(upload.file.read()).decode("utf-8")


def extract_with_ai(image_b64: str) -> List[Dict]:
    """
    Retorna lista de:
    {
      order_id: str,
      protein: str,
      weight_lb: float,
      platform: str
    }
    """

    system_prompt = """
Você é um sistema corporativo do Texas de Brazil.
Extraia apenas PROTEÍNAS dos recibos OLO/Doordash/UberEats.

REGRAS:
- Proteínas válidas: Picanha, Garlic Picanha, Flank Steak, Filet Mignon, Chicken Breast Wrapped in Bacon, Lamb Chops, Sausage, Pork Ribs, Parmesan Pork Loin
- Pesos só podem ser:
  - 1.0 = 1 lb
  - 0.5 = 1/2 lb
- Churrasco Feast = 1 lb PARA CADA PROTEÍNA LISTADA
- Ignore acompanhamentos, bebidas, sobremesas
- Se não houver peso explícito, use:
  - Plate = 0.5 lb por proteína
- Plataforma:
  - Se aparecer Doordash = "DoorDash"
  - Se aparecer Uber = "UberEats"
  - Caso contrário = "OLO"

FORMATO DE SAÍDA JSON:
[
  {
    "order_id": "string",
    "protein": "string",
    "weight_lb": 0.5,
    "platform": "string"
  }
]
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extraia as proteínas desse recibo"},
                    {
                        "type": "input_image",
                        "image_base64": image_b64
                    }
                ]
            }
        ],
        max_output_tokens=500
    )

    raw = response.output_text

    try:
        import json
        return json.loads(raw)
    except:
        return []


def save_rows(store_id: str, rows: List[Dict]):
    db = SessionLocal()
    for r in rows:
        obj = OrderRow(
            store_id=store_id,
            order_id=r.get("order_id", "N/A"),
            protein=r.get("protein", "Unknown"),
            weight_lb=float(r.get("weight_lb", 0)),
            platform=r.get("platform", "Unknown")
        )
        db.add(obj)
    db.commit()
    db.close()


# ==============================
# ROUTES
# ==============================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(store_id: str = Form(...), pin: str = Form(...)):
    if not validate_store_pin(store_id, pin):
        return HTMLResponse("<h3>PIN inválido</h3>", status_code=403)

    return RedirectResponse(
        url=f"/app?store_id={store_id}&pin={pin}",
        status_code=302
    )


@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request, store_id: str, pin: str):
    if not validate_store_pin(store_id, pin):
        return HTMLResponse("<h3>Acesso negado</h3>", status_code=403)

    return templates.TemplateResponse(
        "app.html",
        {
            "request": request,
            "store_id": store_id,
            "pin": pin
        }
    )


@app.post("/upload_ui")
async def upload_ui(
    store_id: str = Form(...),
    pin: str = Form(...),
    file: UploadFile = File(...)
):
    if not validate_store_pin(store_id, pin):
        return HTMLResponse("<h3>PIN inválido</h3>", status_code=403)

    img_b64 = image_to_base64(file)
    rows = extract_with_ai(img_b64)
    save_rows(store_id, rows)

    return RedirectResponse(
        url=f"/app?store_id={store_id}&pin={pin}",
        status_code=302
    )


@app.get("/report.csv")
def report_csv(store_id: str, kind: str, pin: str):
    if not validate_store_pin(store_id, pin):
        return HTMLResponse("Acesso negado", status_code=403)

    db = SessionLocal()
    now = datetime.utcnow()

    if kind == "weekly":
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)

    rows = db.query(OrderRow).filter(
        OrderRow.store_id == store_id,
        OrderRow.timestamp >= start
    ).all()

    db.close()

    data = [
        {
            "Store": r.store_id,
            "OrderID": r.order_id,
            "Protein": r.protein,
            "Weight_LB": r.weight_lb,
            "Platform": r.platform,
            "Timestamp": r.timestamp.isoformat()
        }
        for r in rows
    ]

    df = pd.DataFrame(data)

    stream = df.to_csv(index=False)
    return StreamingResponse(
        iter([stream]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={store_id}_{kind}_report.csv"
        }
    )


@app.get("/forecast.csv")
def forecast_csv(store_id: str, pin: str):
    if not validate_store_pin(store_id, pin):
        return HTMLResponse("Acesso negado", status_code=403)

    db = SessionLocal()
    now = datetime.utcnow()
    start = now - timedelta(days=30)

    rows = db.query(OrderRow).filter(
        OrderRow.store_id == store_id,
        OrderRow.timestamp >= start
    ).all()

    db.close()

    totals = {}
    for r in rows:
        totals[r.protein] = totals.get(r.protein, 0) + r.weight_lb

    forecast_data = []
    for protein, total_lb in totals.items():
        weekly_avg = total_lb / 4
        suggested_order = round(weekly_avg * 1.15, 2)  # 15% buffer
        forecast_data.append({
            "Protein": protein,
            "30_Days_Total_LB": round(total_lb, 2),
            "Weekly_Avg_LB": round(weekly_avg, 2),
            "Suggested_Order_LB": suggested_order
        })

    df = pd.DataFrame(forecast_data)
    stream = df.to_csv(index=False)

    return StreamingResponse(
        iter([stream]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={store_id}_forecast.csv"
        }
    )
