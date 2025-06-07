from sqlalchemy.orm import Session
from app.models.models import Stores

def create_store(db: Session, name: str, website_url: str) -> Stores:
    db_store = Stores(name=name, website_url=website_url)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store