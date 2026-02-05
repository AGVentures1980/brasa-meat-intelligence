from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Store, ItemMap


# =========================================
# SEED LOJA PILOTO — TEXAS DE BRAZIL
# =========================================
def seed_store():

    db: Session = SessionLocal()

    exists = db.query(Store).filter(Store.id == 903).first()

    if exists:
        print("Seed loja já existe — nada foi alterado")
        return

    store = Store(
        id=903,
        store_id=903,
        name="Texas de Brazil - Tampa (Pilot)",
        email="pilot@texasdebrazil.com",
        pin_hash="demo_pin_hash"
    )

    db.add(store)
    db.commit()

    print("Seed loja piloto criada com sucesso")


# =========================================
# SEED ITEM MAP — CONVERSÃO OLO → PROTEÍNA
# =========================================
def seed_item_map():

    db: Session = SessionLocal()

    items = [

        # TEXAS — PRINCIPAIS
        {"raw_item": "Picanha 1 LB", "protein": "picanha", "weight_lb": 1.0},
        {"raw_item": "Filet Mignon 1 LB", "protein": "filet", "weight_lb": 1.0},
        {"raw_item": "Fraldinha 1 LB", "protein": "fraldinha", "weight_lb": 1.0},
        {"raw_item": "Alcatra 1 LB", "protein": "alcatra", "weight_lb": 1.0},

        # COMBOS
        {"raw_item": "Combo 2 Proteins", "protein": "combo_2", "combo_proteins": 2},

    ]

    for i in items:

        exists = db.query(ItemMap).filter(
            ItemMap.raw_item == i["raw_item"]
        ).first()

        if exists:
            continue

        record = ItemMap(
            raw_item=i["raw_item"],
            protein=i.get("protein"),
            weight_lb=i.get("weight_lb"),
            combo_proteins=i.get("combo_proteins")
        )

        db.add(record)

    db.commit()

    print("Seed item_map criado com sucesso")
