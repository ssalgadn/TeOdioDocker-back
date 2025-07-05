from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from .routers import cards, product_router, price_router, store_router, comment_router, review_router
from fastapi.middleware.cors import CORSMiddleware
from .utils.utils import VerifyToken
from app.routers import auth

token_auth_scheme = HTTPBearer()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://tudominiofrontend.vercel.app",
    "https://te-odio-docker-front.vercel.app/",
    "https://te-odio-docker-front-git-main-teodiodockers-projects.vercel.app/"  
]
app = FastAPI()
verifyToken = VerifyToken()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(product_router.router)
app.include_router(price_router.router)
app.include_router(store_router.router)
app.include_router(comment_router.router)
app.include_router(review_router.router)
@app.get("/")
def read_root():
    return {"msg": "Hello World"}