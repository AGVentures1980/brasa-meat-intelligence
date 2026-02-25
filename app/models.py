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
