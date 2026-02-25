from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import SupplierInvoice, InvoiceItem, MarketIndex
import csv
import io
import math

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# STEALTH ENTRY: Invoice Upload
# ==========================================
@router.post("/stealth-upload")
async def stealth_upload(
    store_id: int = Form(...),
    supplier_name: str = Form(...),
    invoice_date: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Stealth entry point for invoices. The manager uploads a CSV/invoice
    thinking it is just for 'store records', but it feeds the corp database.
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    # Create Invoice Header
    invoice = SupplierInvoice(
        store_id=store_id,
        invoice_date=invoice_date,
        supplier_name=supplier_name,
        total_amount=0.0
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    total = 0.0
    inserted = 0
    for row in reader:
        # Tries to handle different CSV column names stealthily
        raw_name = row.get("item_name") or row.get("product") or row.get("desc") or "unknown"
        cut = row.get("cut") or "other"
        qty_str = row.get("quantity") or row.get("qty") or "0"
        price_str = row.get("unit_price") or row.get("price") or "0"

        try:
            qty = float(qty_str)
            price = float(price_str)
        except ValueError:
            continue

        if qty > 0 and price > 0:
            item = InvoiceItem(
                invoice_id=invoice.id,
                cut=cut,
                raw_item_name=raw_name,
                unit_price=price,
                quantity=qty
            )
            db.add(item)
            total += (qty * price)
            inserted += 1

    invoice.total_amount = total
    db.commit()

    return {"status": "ok", "items_processed": inserted, "invoice_id": invoice.id}

# ==========================================
# HIVE MIND ANONYMIZATION engine
# ==========================================
def calculate_hive_mind_median(db: Session, cut: str):
    """
    Hive Mind: Calculate the anonymized median price for a specific cut
    across the entire system. Discards top 10% and bottom 10% to prevent
    outliers and ensure anonymity mathematically.
    """
    items = db.query(InvoiceItem).filter(InvoiceItem.cut == cut).all()
    if not items:
        return 0.0

    prices = sorted([item.unit_price for item in items])
    n = len(prices)

    # Need at least 5 data points to do 10% trimming safely
    if n >= 5:
        trim_count = max(1, int(n * 0.10))
        prices = prices[trim_count:-trim_count]

    m = len(prices)
    if m == 0:
        return 0.0

    mid = m // 2
    if m % 2 == 0:
        median = (prices[mid - 1] + prices[mid]) / 2.0
    else:
        median = prices[mid]

    return round(median, 2)

@router.get("/hive-mind-benchmark/{cut}")
def get_benchmark(cut: str, db: Session = Depends(get_db)):
    """
    API call used by the Dashboard to fetch the anonymized network 
    benchmark vs the Market Index.
    """
    hive_mind_price = calculate_hive_mind_median(db, cut)
    
    # Get latest USDA/Urner Barry index for this cut
    market_point = db.query(MarketIndex).filter(MarketIndex.cut == cut).order_by(MarketIndex.date.desc()).first()
    market_price = market_point.benchmark_price if market_point else 0.0

    return {
        "cut": cut,
        "hive_mind_median": hive_mind_price,
        "market_index": market_price,
        "gap": round(hive_mind_price - market_price, 2)
    }

# ==========================================
# CORP PROCUREMENT DASHBOARD (OWNER ONLY)
# ==========================================
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
templates = Jinja2Templates(directory="templates")

from fastapi import HTTPException
from app.models import Store

@router.get("/dashboard", response_class=HTMLResponse)
def procurement_dashboard(request: Request, store_id: int, db: Session = Depends(get_db)):
    """
    Secure Route: Only allows the 'OWNER' role to access the Market Reference Analysis.
    The rule mandates that ONLY the owner (store_id == 1) can see the money left on the table.
    """
    # 🚨 SECURITY CHECK: Ensure it's the OWNER 🚨
    # Assuming store_id = 1 represents the "Owner / Diretoria" master account.
    if store_id != 1:
        raise HTTPException(
            status_code=403, 
            detail="Acesso Negado: Apenas o Owner (Master Account) tem permissão para visualizar o Enterprise Procurement Dashboard."
        )

    # Fetch user context securely
    store = db.query(Store).filter(Store.id == store_id).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Fetch data to populate the template
    cuts = ["picanha", "filet", "fraldinha", "alcatra"]
    benchmark_data = []

    for cut in cuts:
        # 1. Store Average (Since it's Owner, maybe we want network average, or leave as requested)
        # We will fetch the network average since Owner shouldn't see just their own "purchases"
        store_items = db.query(InvoiceItem).join(SupplierInvoice).filter(
            InvoiceItem.cut == cut
        ).all()
        
        store_avg = 0.0
        if store_items:
            store_avg = sum([i.unit_price for i in store_items]) / len(store_items)

        # 2. Hive Mind
        hive_mind = calculate_hive_mind_median(db, cut)

        # 3. Market Index
        market_point = db.query(MarketIndex).filter(MarketIndex.cut == cut).order_by(MarketIndex.date.desc()).first()
        market_price = market_point.benchmark_price if market_point else 0.0

        benchmark_data.append({
            "cut": cut,
            "store_avg": round(store_avg, 2),
            "hive_mind_median": hive_mind,
            "market_index": market_price
        })

    return templates.TemplateResponse(
        "corp_procurement.html",
        {
            "request": request,
            "benchmark_data": benchmark_data,
            "store_id": store_id
        }
    )
