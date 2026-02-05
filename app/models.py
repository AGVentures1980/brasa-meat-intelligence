from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    order_id = Column(String, index=True)
    item_name = Column(String, index=True)
    qty = Column(Float)
    order_date = Column(Date)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, unique=True, index=True)
    cut = Column(String)
    qty_lb = Column(Float)  # consumo por unidade
