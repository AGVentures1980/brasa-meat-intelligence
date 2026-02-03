from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, unique=True, index=True, nullable=False)   # ex: 901
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)       # email da loja/gerente
    pin_hash = Column(String, nullable=False)                              # hash do PIN (TDB901)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UploadBatch(Base):
    __tablename__ = "upload_batches"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    source = Column(String, default="OLO_CSV")   # futuro: OLO_API
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    original_filename = Column(String, nullable=True)
    status = Column(String, default="processed")  # processed / needs_review
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ItemMap(Base):
    """
    Mapeia o nome do item do CSV -> proteína + peso (lb).
    Ex: "Picanha - 1 LB" -> protein="picanha", weight_lb=1.0
        "Combo - 0.5LB (2 proteins)" -> protein="combo_2", weight_lb=0.5 (tratamento especial)
    """
    __tablename__ = "item_map"
    id = Column(Integer, primary_key=True, index=True)
    raw_item = Column(String, unique=True, index=True, nullable=False)
    protein = Column(String, nullable=True)          # se null => ignorar (não é proteína)
    weight_lb = Column(Float, nullable=True)         # 0.5 ou 1.0 ou null
    combo_proteins = Column(Integer, nullable=True)  # se combo, quantas proteínas (ex: 2)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderLine(Base):
    __tablename__ = "order_lines"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    upload_batch_id = Column(Integer, ForeignKey("upload_batches.id"), nullable=False)

    order_id = Column(String, index=True, nullable=True)    # ID grande do OLO
    order_dt = Column(DateTime(timezone=True), nullable=True)

    raw_item = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    protein = Column(String, nullable=True)                 # já normalizado
    weight_lb = Column(Float, nullable=True)                # 0.5 ou 1.0
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
