from fastapi import FastAPI
from .routers import cards, product_router, price_router, store_router
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://tudominiofrontend.vercel.app",
    "https://te-odio-docker-front.vercel.app/",
    "https://te-odio-docker-front-git-main-teodiodockers-projects.vercel.app/"  
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(product_router.router)
app.include_router(price_router.router)
app.include_router(store_router.router)

@app.get("/")
def read_root():
    return {"msg": "Hello World"}
