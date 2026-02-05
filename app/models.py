from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from app.database import Base
from datetime import date

class MeatUsage(Base):
    __tablename__ = "meat_usage"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)
    cut = Column(String(100), nullable=False)
    received_qty = Column(Numeric(10,2), nullable=False)
    used_qty = Column(Numeric(10,2), nullable=False)
    waste_qty = Column(Numeric(10,2), nullable=False)
    record_date = Column(Date, default=date.today)
