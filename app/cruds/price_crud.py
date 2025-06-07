from sqlalchemy.orm import Session
from app.models.models import Prices, Products

def create_price(db: Session, product_id: int, store_id: int, price: int, url: str) -> Prices:
    db_price = Prices(
        product_id=product_id,
        store_id=store_id,
        price=price,
        url=url
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)

    product = db.query(Products).filter(Products.id == product_id).first()
    if product and (product.min_price is None or price < product.min_price):
        product.min_price = price
        db.commit()
        db.refresh(product)
        
    return db_price