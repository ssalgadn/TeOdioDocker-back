from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schema.product_schemas import (
    StoreBase,
    StoreCreate
)
from app.cruds.store_crud import (
    create_store
)

from app.database import get_db

router = APIRouter(prefix="/stores", tags=["stores"])

@router.post("/", response_model=StoreBase, status_code=201)
async def create_store_endpoint(
    store: StoreCreate,
    db: Session = Depends(get_db)
):
    db_store = create_store(db=db, name=store.name, website_url=store.website_url)
    return StoreBase.model_validate(db_store)
