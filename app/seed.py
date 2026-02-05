from app.database import SessionLocal
from app.models import Store, Recipe
from app.security import hash_pin


def run_seed():
    db = SessionLocal()

    # Loja piloto
    store = Store(
        store_id=903,
        name="Texas de Brazil - Tampa",
        email="tampa@tdb.com",
        pin_hash=hash_pin("903"),
        active=1
    )

    db.add(store)

    # Receita básica rodizio
    recipes = [
        ("Rodizio Dinner", "Picanha", 0.35),
        ("Rodizio Dinner", "Filet", 0.20),
        ("Rodizio Dinner", "Alcatra", 0.25),
        ("Rodizio Dinner", "Fraldinha", 0.18),
    ]

    for item, cut, qty in recipes:
        db.add(Recipe(
            store_id=903,
            item_name=item,
            cut=cut,
            qty_per_unit=qty
        ))

    db.commit()
    db.close()
