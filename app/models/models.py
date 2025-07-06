from datetime import datetime
from sqlalchemy import Column, DateTime, func
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from enum import Enum

class GameEnum(str, Enum):
    POKEMON = "pokemon"
    YUGIOH = "yugioh"
    MAGIC = "magic"
    OTHER = "other"

class ProductTypeEnum(str, Enum):
    BOOSTER = "booster"
    SINGLES = "singles"
    BUNDLE = "bundle"
    OTHER = "other"

class Stores(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    website_url: str = Field(nullable=False, max_length=255)

    prices: List["Prices"] = Relationship(back_populates="store")
    reviews: List["Reviews"] = Relationship(back_populates="store")

class Products(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    img_url: str | None = Field(default=None, max_length=255)
    min_price: int | None = Field(default=None)
    game: str = Field(max_length=255, nullable=False)
    edition: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    condition: str | None = Field(default=None, max_length=20)
    product_type: str = Field(max_length=20, nullable=False)

    
    prices: List["Prices"] = Relationship(back_populates="product")
    comments: List["Comments"] = Relationship(back_populates="product")

class Prices(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    store_id: int = Field(foreign_key="stores.id", nullable=False)
    price: int = Field(nullable=False)
    url: str = Field(max_length=255, nullable=False)
    scrapped_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))

    product: Optional[Products] = Relationship(back_populates="prices")
    store: Optional[Stores] = Relationship(back_populates="prices")

class Comments(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str = Field(nullable=False, max_length=255)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    text: str = Field(nullable=False, max_length=500)
    date: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))

    product: Optional[Products] = Relationship(back_populates="comments")

class Reviews(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str = Field(nullable=False, max_length=255)
    store_id: int = Field(foreign_key="stores.id", nullable=False)
    rating: int = Field(ge=1, le=5, nullable=False)  # Rating between 1 and 5
    date: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))

    store: Optional[Stores] = Relationship(back_populates="reviews")
