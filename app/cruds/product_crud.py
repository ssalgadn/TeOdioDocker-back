from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.models import Products, GameEnum, ProductTypeEnum

def get_products(
    db: Session,
    name: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    game: Optional[GameEnum] = None,
    product_type: Optional[ProductTypeEnum] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Products]:
    query = db.query(Products)

    filters = []

    if name:
        filters.append(Products.name.ilike(f"%{name}%"))

    if min_price is not None:
        filters.append(Products.min_price >= min_price)

    if max_price is not None:
        filters.append(Products.min_price <= max_price) # ASUMO que filtraremos por min_price del producto

    if game:
        filters.append(Products.game == game)
    
    if product_type:
        filters.append(Products.product_type == product_type)

    if filters:
        query = query.filter(and_(*filters))

    return query.offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Optional[Products]:
    return db.query(Products).filter(Products.id == product_id).first()

def create_product(
    db: Session,
    name: str,
    game: GameEnum,
    product_type: ProductTypeEnum,
    img_url: Optional[str] = None,
    min_price: Optional[int] = None,
    edition: Optional[str] = None,
    language: Optional[str] = None,
    description: Optional[str] = None,
    condition: Optional[str] = None,
) -> Products:
    db_product = Products(
        name=name,
        img_url=img_url,
        min_price=min_price,
        game=game,
        edition=edition,
        language=language,
        description=description,
        condition=condition,
        product_type=product_type
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_products_bulk(
    db: Session,
    products: List[Products]
) -> List[Products]:
    db_products = []
    
    for product in products:
        db_product = Products(
            name=product.name,
            img_url=product.img_url,
            min_price=product.min_price,
            game=product.game,
            edition=product.edition,
            language=product.language,
            description=product.description,
            condition=product.condition,
            product_type=product.product_type
        )
        db_products.append(db_product)
    
    db.add_all(db_products)
    db.commit()
    
    for product in db_products:
        db.refresh(product)
    
    return db_products