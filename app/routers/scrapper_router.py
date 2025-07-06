from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse
from typing import List

from app.schema.scrapper_schemas import ScrapperItem
from app.cruds.store_crud import create_store
from app.cruds.product_crud import create_product
from app.cruds.price_crud import create_price
from app.models.models import Stores, Products, Prices, GameEnum, ProductTypeEnum
from app.database import get_db

router = APIRouter(prefix="/scrapper", tags=["scrapper"])

def map_game_to_enum(game: str) -> GameEnum:
    game_mapping = {
        "pokemon": GameEnum.POKEMON,
        "magic-the-gathering": GameEnum.MAGIC,
        "yu-gi-oh": GameEnum.YUGIOH,
        "prismatic_evolutions": GameEnum.POKEMON,
        "twilight_masquerade": GameEnum.POKEMON,
        "temporal_forces": GameEnum.POKEMON
    }
    return game_mapping.get(game.lower(), GameEnum.OTHER)

def map_product_type_to_enum(product_type: str) -> ProductTypeEnum:
    type_mapping = {
        "booster": ProductTypeEnum.BOOSTER,
        "singles": ProductTypeEnum.SINGLES,
        "bundle": ProductTypeEnum.BUNDLE
    }
    return type_mapping.get(product_type.lower(), ProductTypeEnum.OTHER)

def extract_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def get_or_create_store(db: Session, store_name: str, website_url: str) -> Stores:
    store = db.query(Stores).filter(Stores.name == store_name).first()
    if not store:
        store = create_store(db=db, name=store_name, website_url=website_url)
    return store

def create_price_from_scrapper(db: Session, item: ScrapperItem, product_id: int, store_id: int):
    return create_price(
            db=db,
            product_id=product_id,
            store_id=store_id,
            price=item.price,
            url=item.url
        )

def get_or_create_product(db: Session, item: ScrapperItem) -> Products:
    product = db.query(Products).filter(Products.name == item.name).first()
    if not product:
        product = create_product(
            db=db,
            name=item.name,
            game=map_game_to_enum(item.game),
            product_type=map_product_type_to_enum(item.product_type),
            img_url=item.img_url if item.img_url else None,
            min_price=item.min_price,
            language=item.language,
            description=item.description
        )
    return product

@router.post("/bulk")
async def process_scrapper_results(
    items: List[ScrapperItem],
    db: Session = Depends(get_db)
):
    processed_count = 0
    errors = []
    
    for item in items:
        try:
            website_url = extract_base_url(item.url)
            
            store = get_or_create_store(db, item.store, website_url)
            product = get_or_create_product(db, item)
            
            create_price_from_scrapper(db, item, product.id, store.id)
            
            processed_count += 1
            
        except SQLAlchemyError as e:
            errors.append(f"Error processing item '{item.name}': {str(e)}")
            db.rollback()
        except Exception as e:
            errors.append(f"Unexpected error processing item '{item.name}': {str(e)}")
    
    response = {
        "message": f"Successfully processed {processed_count} items",
        "processed_count": processed_count,
        "total_items": len(items)
    }
    
    if errors:
        response["errors"] = errors
        response["error_count"] = len(errors)
    
    return response
