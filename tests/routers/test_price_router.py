from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from app.main import app
from app.database import get_db
from app.models.models import Products, Stores, Prices


@pytest.fixture
def client(db: Session):
    def override_get_db_for_test():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db_for_test
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture
def test_product(db: Session):
    product = Products(name="Test Product", game="Test Game", product_type="Card")
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def test_store(db: Session):
    store = Stores(name="Test Store", website_url="https://teststore.com")
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def test_create_price_endpoint_product_not_found(client: TestClient, test_store: Stores):
    price_data = {
        "product_id": 999,
        "store_id": test_store.id,
        "price": 1500,
        "url": "https://teststore.com/product/999"
    }

    response = client.post("/prices/", json=price_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_price_endpoint_store_not_found(client: TestClient, test_product: Products):
    price_data = {
        "product_id": test_product.id,
        "store_id": 999,
        "price": 1500,
        "url": "https://teststore.com/product/1"
    }

    response = client.post("/prices/", json=price_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Store not found"}
