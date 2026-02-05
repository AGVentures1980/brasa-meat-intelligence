@router.post("/upload-orders")
async def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    inserted = 0

    for row in reader:

        record = Order(
            store_id=int(row.get("store_id") or row.get("Store ID")),
            order_id=row.get("order_id") or row.get("Order ID"),
            item=row.get("item") or row.get("Menu Item"),
            qty=float(row.get("qty") or row.get("Quantity")),
            order_date=row.get("order_date") or row.get("Date")
        )

        db.add(record)
        inserted += 1

    db.commit()

    return {
        "status": "ok",
        "rows_inserted": inserted
    }
