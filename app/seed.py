from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Store
from app.security import hash_pin

def run():
    init_db()
    db: Session = SessionLocal()

    # LOJA PILOTO — TEXAS DE BRAZIL
    store_id = 903
    name = "Texas de Brazil - Tampa (Pilot)"
    email = "tampa@texasdebrazil.com"

    # PIN FINAL — TEM QUE SER IGUAL AO STRICT_STORE_PIN DO RENDER
    pin_plain = "TDB903"

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
        print("Seed criado com sucesso")
    else:
        print("Seed já existe — nada foi alterado")

    db.close()

if __name__ == "__main__":
    run()
