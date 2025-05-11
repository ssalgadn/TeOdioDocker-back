from fastapi import APIRouter
router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_cards():
    return [
  { "id": 1, "name": "Charizard VMAX", "price": 24990, "store": "Tienda Friki", "image": "https://mesa1.cl/cdn/shop/products/981fb977-e4a7-45bc-b61c-f9164b19b64e_c6cdc997-1c21-41ec-ac5b-e82d32ae806f.png?v=1696303525" },
  { "id": 2, "name": "Blue-Eyes White Dragon", "price": 18990, "store": "Geeklandia", "image": "https://via.placeholder.com/200x300?text=Blue-Eyes" },
  { "id": 3, "name": "Dark Magician", "price": 21990, "store": "Mundo Duelista", "image": "https://via.placeholder.com/200x300?text=Magician" },
  { "id": 4, "name": "Pikachu Holo", "price": 12990, "store": "CardZone", "image": "https://via.placeholder.com/200x300?text=Pikachu" },
  { "id": 5, "name": "Mewtwo GX", "price": 15990, "store": "Cartas Top", "image": "https://via.placeholder.com/200x300?text=Mewtwo" },
  { "id": 6, "name": "One Piece Luffy Rare", "price": 28990, "store": "LuffyStore", "image": "https://via.placeholder.com/200x300?text=Luffy" },
]
