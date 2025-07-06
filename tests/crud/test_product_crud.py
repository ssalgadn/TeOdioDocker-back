
from sqlalchemy.orm import Session
from typing import List
from app.cruds.product_crud import (
    get_products,
    get_product_by_id,
    create_product,
    create_products_bulk
)
from app.models.models import Products

def test_create_product(db: Session):
    product_data = {
        "name": "Test Product",
        "game": "Test Game",
        "product_type": "Card",
        "description": "A test product",
        "price": 100
    }

    created_product = create_product(
        db=db,
        name=product_data["name"],
        game=product_data["game"],
        product_type=product_data["product_type"],
        description=product_data["description"],
    )

    assert created_product is not None
    assert created_product.name == product_data["name"]
    assert created_product.game == product_data["game"]
    assert created_product.product_type == product_data["product_type"]
    assert created_product.description == product_data["description"]
    assert created_product.id is not None

def test_get_product_by_id(db: Session):
    product = create_product(db, name="FindMe", game="TestGame", product_type="TestType")

    found_product = get_product_by_id(db, product.id)
    not_found_product = get_product_by_id(db, 9999)


    assert found_product is not None
    assert found_product.id == product.id
    assert found_product.name == "FindMe"
    assert not_found_product is None

def test_get_products(db: Session):
    create_product(db, name="Product A", game="Game 1", product_type="Type X", min_price=10)
    create_product(db, name="Product B", game="Game 1", product_type="Type Y", min_price=20)
    create_product(db, name="Product C", game="Game 2", product_type="Type X", min_price=30)
    create_product(db, name="Another A", game="Game 2", product_type="Type Z", min_price=40)

    all_products = get_products(db)
    assert len(all_products) == 4

    a_products = get_products(db, name="A")
    assert len(a_products) == 2
    assert all(p.name in ["Product A", "Another A"] for p in a_products)

    game1_products = get_products(db, game="Game 1")
    assert len(game1_products) == 2

    typex_products = get_products(db, product_type="Type X")
    assert len(typex_products) == 2

    price_gt_25 = get_products(db, min_price=25)
    assert len(price_gt_25) == 2

    price_lt_25 = get_products(db, max_price=25)
    assert len(price_lt_25) == 2

    combo_products = get_products(db, name="Product", game="Game 1", min_price=15)
    assert len(combo_products) == 1
    assert combo_products[0].name == "Product B"

    paginated_products = get_products(db, skip=1, limit=2)
    assert len(paginated_products) == 2
    assert paginated_products[0].name == "Product B"
    assert paginated_products[1].name == "Product C"

def test_create_products_bulk(db: Session):
    products_to_create = [
        Products(name="Bulk 1", game="Bulk Game", product_type="Bulk Type"),
        Products(name="Bulk 2", game="Bulk Game", product_type="Bulk Type"),
    ]

    created_products = create_products_bulk(db, products_to_create)

    assert len(created_products) == 2
    assert created_products[0].id is not None
    assert created_products[1].id is not None

    all_products = get_products(db, game="Bulk Game")
    assert len(all_products) == 2
