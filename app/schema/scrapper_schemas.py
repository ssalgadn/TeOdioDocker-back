from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class ScrapperItem(BaseModel):
    price: int
    description: Optional[str] = None
    language: Optional[str] = None
    stock: Union[Dict[str, Any], str] = None
    name: str
    url: str
    game: str
    timestamp: str
    store: str
    product_type: str
    img_url: Optional[str] = None
    min_price: int

class ScrapperRequest(BaseModel):
    results: List[ScrapperItem]
