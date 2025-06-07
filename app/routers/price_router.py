from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schema.product_schemas import (
    PriceResponse,
    PriceCreate
)
from app.cruds.product_crud import get_product_by_id
from app.cruds.price_crud import create_price
from app.models.models import Stores


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