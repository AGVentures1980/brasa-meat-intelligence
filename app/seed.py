import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Store
from app.security import hash_pin

def run():
    init_db()
    db: Session = SessionLocal()

    # EXEMPLO: troque para sua loja piloto
    store_id = 903  # exemplo
    name = "Texas de Brazil - Tampa (Pilot)"
    email = "tampa@texasdebrazil.com"  # troque para o email real que você vai usar
    pin_plain = f"TDB{store_id}"

    exists = db.query(Store).filter(Store.store_id == store_id).first()
    if not exists:
        s = Store(
            store_id=store_id,
            name=name,
            email=email,
            pin_hash=hash_pin(pin_plain),
            active=True
        )
        db.add(s)
        db.commit()

    db.close()
    print("Seed OK")

if __name__ == "__main__":
    run()
