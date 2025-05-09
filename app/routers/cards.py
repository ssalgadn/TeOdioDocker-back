from fastapi import APIRouter
router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_cards():
    return [{"id": 1,
    "name": 'Charizard VMAX',
    "image": 'https://assets.pokemon.com/static-assets/content-assets/cms2-es-xl/img/cards/web/SWSH45/SWSH45_LA_SV107.png',
    "generalInfo": {
      "setName": 'Sword & Shield: Darkness Ablaze',
      "cardNumber": '020/189',
      "rarity": 'VMAX Rare',
      "category": 'Pokémon',
      "releaseDate": '2020-08-14',
      "description": 'Carta Pokémon Charizard VMAX de la expansión Sword & Shield: Darkness Ablaze. Una de las cartas más buscadas de la colección.',
    }}]
