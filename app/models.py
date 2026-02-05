class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer)
    order_id = Column(String)
    item_name = Column(String)
    qty = Column(Float)
    order_date = Column(DateTime)
