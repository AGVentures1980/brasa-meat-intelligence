from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import SupplierInvoice, InvoiceItem, MarketIndex
import random
from datetime import datetime, timedelta

def seed_stealth_procurement():
    db: Session = SessionLocal()

    # Avoid duplicating seed
    if db.query(MarketIndex).first():
        print("Stealth Procurement data already seeded - SKIPPED.")
        return

    print("Seeding USDA Market Indices...")
    # Seed Market Index (Baseline for last week)
    indices = [
        MarketIndex(date="2026-02-20", cut="picanha", source="USDA", benchmark_price=6.10),
        MarketIndex(date="2026-02-20", cut="filet", source="USDA", benchmark_price=12.50),
        MarketIndex(date="2026-02-20", cut="fraldinha", source="USDA", benchmark_price=5.80),
        MarketIndex(date="2026-02-20", cut="alcatra", source="USDA", benchmark_price=5.20),
    ]
    db.add_all(indices)
    db.commit()

    print("Seeding Stealth Supplier Invoices for the network (Hive Mind setup)...")
    
    # Store IDs: 903 (Tampa/Pilot), 904 (Addison), 905 (Dallas)
    stores = [903, 904, 905, 906, 907, 908, 909] # Add some dummy stores for math anonymity
    
    cuts_baseline = {
        "picanha": 6.20,
        "filet": 12.80,
        "fraldinha": 5.95,
        "alcatra": 5.30
    }

    inserted_items = 0

    for store_id in stores:
        # Create an invoice for last 3 weeks
        for weeks_ago in range(3):
            inv_date = (datetime.now() - timedelta(days=(weeks_ago * 7) + random.randint(0,4))).strftime("%Y-%m-%d")
            
            invoice = SupplierInvoice(
                store_id=store_id,
                invoice_date=inv_date,
                supplier_name=f"Sysco/US Foods Vendor #{random.randint(10,99)}",
                total_amount=0.0
            )
            db.add(invoice)
            db.commit()
            db.refresh(invoice)

            total = 0.0
            for cut, base_price in cuts_baseline.items():
                # Randomize price slightly. Store 903 (Pilot) will pay slightly higher than the network average 
                # to show an "Opportunity Gap" in the dashboard.
                variance = random.uniform(-0.50, 0.40)
                
                if store_id == 903:
                    # Let's make the pilot store pay exactly $0.45 more than average for Picanha consistently
                    if cut == "picanha":
                        variance = 0.45
                    elif cut == "filet":
                        variance = 0.80 # Overpaying heavily

                unit_price = round(base_price + variance, 2)
                qty = round(random.uniform(50, 300), 2)
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    cut=cut,
                    raw_item_name=f"BOX {cut.upper()} CHF",
                    unit_price=unit_price,
                    quantity=qty
                )
                db.add(item)
                total += (unit_price * qty)
                inserted_items += 1
            
            invoice.total_amount = total
            db.commit()

    print(f"Procurement Seed Complete: Created {inserted_items} stealth invoice items across {len(stores)} stores.")

if __name__ == "__main__":
    seed_stealth_procurement()
