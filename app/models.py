from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime

class MeatUsage(Base):
    __tablename__ = "meat_usage"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    cut = Column(String)
    received_qty = Column(Float)
    used_qty = Column(Float)
    waste_qty = Column(Float)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    order_id = Column(String)
    item = Column(String)
    qty = Column(Float)
    order_date = Column(String)

# ==============================
# PROCUREMENT (PHASE 2 - STEALTH)
# ==============================

class SupplierInvoice(Base):
    __tablename__ = "supplier_invoices"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    invoice_date = Column(String)  # format YYYY-MM-DD
    supplier_name = Column(String) # Optionally encrypted or generic
    total_amount = Column(Float)

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer) # Logical ForeignKey to supplier_invoices.id
    cut = Column(String, index=True) # Normalized cut name like "picanha"
    raw_item_name = Column(String) # What came on the invoice "X BR PL PICA"
    unit_price = Column(Float) # Price per LB or KG
    quantity = Column(Float)

class MarketIndex(Base):
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True) # format YYYY-MM-DD
    cut = Column(String, index=True)
    source = Column(String) # e.g., "USDA" or "Urner Barry"
    benchmark_price = Column(Float)
