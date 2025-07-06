from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse
from typing import List
import requests
import os

from dotenv import load_dotenv
from app.schema.scrapper_schemas import ScrapperItem
from app.cruds.store_crud import create_store
from app.cruds.product_crud import create_product
from app.cruds.price_crud import create_price
from app.models.models import Stores, Products, Prices, GameEnum, ProductTypeEnum
from app.database import get_db
from app.utils.s3_utils import S3ImageService

load_dotenv()

router = APIRouter(prefix="/scrapper", tags=["scrapper"])

s3_service = S3ImageService(
    bucket_name='teodiodocker-images',
    region_name='us-east-2',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

def map_game_to_enum(game: str) -> GameEnum:
    game_mapping = {
        "pokemon": GameEnum.POKEMON,
        "magic": GameEnum.MAGIC,
        "magic-the-gathering": GameEnum.MAGIC,
        "yu-gi-oh": GameEnum.YUGIOH,
        "yugioh": GameEnum.YUGIOH,
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

def download_image_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content

def upload_img_from_url(url: str, filename: str, game_prefix: str) -> str:
    image_bytes = download_image_bytes(url)
    result = s3_service.upload_from_bytes(image_bytes, filename, game_prefix)
    if not result["success"]:
        raise Exception(f"Upload failed: {result['error']}")
    return f"https://teodiodocker-images.s3.us-east-2.amazonaws.com/{result['object_key']}"

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

            img_s3_url = None
            if item.img_url:
                filename = f"{item.name.lower().replace(' ', '_')}.png"
                game_prefix = item.game.lower().replace(" ", "_")
                img_s3_url = upload_img_from_url(item.img_url, filename, game_prefix)

            product = db.query(Products).filter(Products.name == item.name).first()
            if not product:
                product = create_product(
                    db=db,
                    name=item.name,
                    game=map_game_to_enum(item.game),
                    product_type=map_product_type_to_enum(item.product_type),
                    img_url=img_s3_url,
                    min_price=item.min_price,
                    language=item.language,
                    description=item.description
                )

            create_price_from_scrapper(db, item, product.id, store.id)
            processed_count += 1

        except SQLAlchemyError as e:
            errors.append(f"DB error for item '{item.name}': {str(e)}")
            db.rollback()
        except Exception as e:
            errors.append(f"Error for item '{item.name}': {str(e)}")

    response = {
        "message": f"Successfully processed {processed_count} items",
        "processed_count": processed_count,
        "total_items": len(items)
    }

    if errors:
        response["errors"] = errors
        response["error_count"] = len(errors)

    return response
