from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer
from .routers import cards
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

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result

# new code 👇
@app.get("/api/private")
def private(auth_result: str = Security(verifyToken.verify)): # 👈 Use Security and the verify method to protect your endpoints
    """A valid access token is required to access this route"""
    return auth_result