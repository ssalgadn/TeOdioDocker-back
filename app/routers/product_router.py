from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.schema.product_schemas import (
    ProductResponse, 
    ProductWithPricesResponse, 
    PriceWithStore,
    StoreBase,
    ProductCreate
)
from app.schema.comment_schemas import CommentResponse
from app.cruds.product_crud import (
    get_products, 
    get_product_by_id,
    create_product,
    create_products_bulk
)
from app.cruds.comment_crud import get_all_comments_by_product_id
from app.models.models import Prices, Stores, GameEnum, ProductTypeEnum

from app.database import get_db

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
async def get_products_endpoint(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    game: Optional[GameEnum] = Query(None),
    product_type: Optional[ProductTypeEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    products = get_products(
        db=db,
        name=name,
        min_price=min_price,
        max_price=max_price,
        game=game,
        product_type=product_type,
        skip=skip,
        limit=limit
    )

    return [ProductResponse.model_validate(product) for product in products]

@router.get("/{product_id}", response_model=ProductWithPricesResponse)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    latest_prices_subquery = (
        db.query(
            Prices.store_id,
            func.max(Prices.scrapped_at).label('max_scrapped_at')
        )
        .filter(Prices.product_id == product_id)
        .group_by(Prices.store_id)
        .subquery()
    )

    prices_query = (
        db.query(Prices, Stores)
        .join(Stores, Prices.store_id == Stores.id)
        .join(
            latest_prices_subquery, 
            (Prices.store_id == latest_prices_subquery.c.store_id) & 
            (Prices.scrapped_at == latest_prices_subquery.c.max_scrapped_at)
        )
        .filter(Prices.product_id == product_id)
        .all()
    )

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
    product_comments = get_all_comments_by_product_id(db=db, product_id=product_id)
    product_comments = [CommentResponse.model_validate(comment) for comment in product_comments]
    product_response = ProductWithPricesResponse(
        id=product.id,
        name=product.name,
        img_url=product.img_url,
        min_price=product.min_price,
        game=product.game,
        edition=product.edition,
        language=product.language,
        description=product.description,
        condition=product.condition,
        product_type=product.product_type,
        prices=prices_with_stores,
        comments=product_comments
    )

    return product_response

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product_endpoint(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    db_product = create_product(
        db=db,
        name=product.name,
        game=product.game,
        product_type=product.product_type,
        img_url=product.img_url,
        min_price=product.min_price,
        edition=product.edition,
        language=product.language,
        description=product.description,
        condition=product.condition
    )
    return ProductResponse.model_validate(db_product)

@router.post("/createAll", response_model=List[ProductResponse], status_code=201)
async def create_products_bulk_endpoint(
    products: List[ProductCreate],
    db: Session = Depends(get_db)
):
    db_products = create_products_bulk(db=db, products=products)
    return [ProductResponse.model_validate(product) for product in db_products]