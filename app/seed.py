from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Store, Recipe


# ==============================
# SEED STORE — TEXAS PILOT
# ==============================
def seed_store():

    db: Session = SessionLocal()

    store_exists = db.query(Store).filter(Store.id == 903).first()

    if store_exists:
        print("Seed já existe — nada foi alterado")
        return

    store = Store(
        id=903,
        name="Texas de Brazil - Tampa (Pilot)"
    )

    db.add(store)
    db.commit()

    print("Seed loja piloto criada com sucesso")


# ==============================
# SEED RECIPES — PADRÃO
# ==============================
def seed_recipes():

    db: Session = SessionLocal()

    recipes = [
        {"item": "Picanha", "cut": "Picanha", "yield_pct": 0.85},
        {"item": "Filet Mignon", "cut": "Filet", "yield_pct": 0.90},
        {"item": "Fraldinha", "cut": "Fraldinha", "yield_pct": 0.80},
        {"item": "Alcatra", "cut": "Alcatra", "yield_pct": 0.82},
    ]

    for r in recipes:

        exists = db.query(Recipe).filter(Recipe.item == r["item"]).first()

        if exists:
            continue

        recipe = Recipe(
            item=r["item"],
            cut=r["cut"],
            yield_pct=r["yield_pct"]
        )

        db.add(recipe)

    db.commit()

    print("Seed receitas criado")
