from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schema.product_schemas import (
    PriceResponse,
    PriceCreate,
    PriceWithStore,
    StoreBase
)
from app.cruds.product_crud import get_product_by_id
from app.cruds.price_crud import create_price
from app.models.models import Stores, Prices

from app.database import get_db

router = APIRouter(prefix="/prices", tags=["prices"])

@router.post("/", response_model=PriceResponse, status_code=201)
async def create_price_endpoint(
    price: PriceCreate,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db=db, product_id=price.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    store = db.query(Stores).filter(Stores.id == price.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    db_price = create_price(
        db=db,
        product_id=price.product_id,
        store_id=price.store_id,
        price=price.price,
        url=price.url
    )
    return PriceResponse.model_validate(db_price)

@router.get("/product/{product_id}", response_model=List[PriceWithStore])
async def get_prices_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    store_id: Optional[int] = Query(None)
):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = (
        db.query(Prices, Stores)
        .join(Stores, Prices.store_id == Stores.id)
        .filter(Prices.product_id == product_id)
    )

    if store_id:
        store = db.query(Stores).filter(Stores.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        query = query.filter(Prices.store_id == store_id)

    prices_query = query.order_by(Prices.scrapped_at.desc()).all()

    prices_with_stores = []
    for price, store in prices_query:
        price_with_store = PriceWithStore(
            id=price.id,
            price=price.price,
            url=price.url,
            scrapped_at=price.scrapped_at,
            store=StoreBase(
                id=store.id,
                name=store.name,
                website_url=store.website_url
            )
        )
        prices_with_stores.append(price_with_store)

    return prices_with_stores
