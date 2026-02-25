from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Store


def seed_store():
    db: Session = SessionLocal()

    store_exists = db.query(Store).filter(Store.id == 903).first()
    if store_exists:
        print("Seed loja SKIPPED — já existe")
        return

    store = Store(
        id=903,
        store_id=903,
        name="Texas de Brazil - Tampa (Pilot)",
        email="tampa@texasdebrazil.com",
        pin_hash="TEMP",
        active=True
    )

    db.add(store)
    db.commit()

    print("Seed loja piloto criada com sucesso")

