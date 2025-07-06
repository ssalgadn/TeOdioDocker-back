from sqlalchemy.orm import Session
from app.cruds.price_crud import create_price
from app.models.models import Products, Stores

def test_create_price_with_no_min_price(db: Session):
    product = Products(name="Test Product", description="A product for testing", game="Test Game", product_type="Test Type")
    store = Stores(name="Test Store", website_url="http://teststore.com")
    db.add(product)
    db.add(store)
    db.commit()
    db.refresh(product)
    db.refresh(store)

    new_price = create_price(db, product_id=product.id, store_id=store.id, price=100, url="http://teststore.com/product")

    db.refresh(product)
    assert new_price.price == 100
    assert new_price.product_id == product.id
    assert product.min_price == 100

def test_create_price_lower_than_min_price(db: Session):
    product = Products(name="Test Product 2", description="Another product", game="Test Game", product_type="Test Type", min_price=200)
    store = Stores(name="Test Store 2", website_url="http://teststore2.com")
    db.add(product)
    db.add(store)
    db.commit()
    db.refresh(product)
    db.refresh(store)

    new_price = create_price(db, product_id=product.id, store_id=store.id, price=150, url="http://teststore2.com/product")

    db.refresh(product)
    assert new_price.price == 150
    assert product.min_price == 150

def test_create_price_higher_than_min_price(db: Session):
    product = Products(name="Test Product 3", description="Yet another product", game="Test Game", product_type="Test Type", min_price=300)
    store = Stores(name="Test Store 3", website_url="http://teststore3.com")
    db.add(product)
    db.add(store)
    db.commit()
    db.refresh(product)
    db.refresh(store)

    new_price = create_price(db, product_id=product.id, store_id=store.id, price=350, url="http://teststore3.com/product")

    db.refresh(product)
    assert new_price.price == 350
    assert product.min_price == 300
