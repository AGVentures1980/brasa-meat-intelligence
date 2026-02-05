from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


# =========================
# STORES
# =========================

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    name = Column(String)
    email = Column(String)
    pin_hash = Column(String)
    active = Column(Integer)


# =========================
# PEDIDOS IMPORTADOS
# =========================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    item_name = Column(String)
    qty = Column(Float)
    order_date = Column(Date)


# =========================
# RECEITA DE CARNE
# =========================

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer)
    item_name = Column(String)
    cut = Column(String)
    qty_per_unit = Column(Float)
