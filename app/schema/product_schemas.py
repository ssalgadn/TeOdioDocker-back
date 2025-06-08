from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class StoreBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    website_url: str

class StoreCreate(BaseModel):
    name: str
    website_url: str

class PriceWithStore(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    price: int
    url: str
    scrapped_at: datetime
    store: StoreBase

class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    img_url: Optional[str] = None
    min_price: Optional[int] = None
    game: str
    edition: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    product_type: str

class ProductCreate(BaseModel):
    name: str
    img_url: Optional[str] = None
    min_price: Optional[int] = None
    game: str
    edition: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    product_type: str

class ProductResponse(ProductBase):
    pass

class ProductWithPricesResponse(ProductBase):
    prices: List[PriceWithStore] = []

class PriceCreate(BaseModel):
    product_id: int
    store_id: int
    price: int
    url: str

class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    store_id: int
    price: int
    url: str
    scrapped_at: datetime
