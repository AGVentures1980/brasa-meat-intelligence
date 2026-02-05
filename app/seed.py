from app.models import Recipe
from app.database import SessionLocal

def seed_recipes():
    db = SessionLocal()

    recipes = [
        ("Picanha Sandwich", "Picanha", 0.25),
        ("Filet Mignon Plate", "Filet", 0.40),
        ("Ribeye Plate", "Ribeye", 0.50),
    ]

    for item, cut, qty in recipes:
        exists = db.query(Recipe).filter_by(item_name=item).first()
        if not exists:
            db.add(Recipe(item_name=item, cut=cut, qty_lb=qty))

    db.commit()
    db.close()
