from sqlalchemy.orm import Session
from app.cruds.store_crud import create_store
from app.models.models import Stores

def test_create_store(db: Session):
    store_name = "My Test Store"
    store_url = "https://www.teststore.com"

    new_store = create_store(db, name=store_name, website_url=store_url)

    assert new_store is not None
    assert new_store.name == store_name
    assert new_store.website_url == store_url
    assert new_store.id is not None

    queried_store = db.query(Stores).filter(Stores.id == new_store.id).first()
    assert queried_store is not None
    assert queried_store.name == store_name
