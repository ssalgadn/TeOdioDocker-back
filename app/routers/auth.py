from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

class AuthRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(auth: AuthRequest):
    data = {
        "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
        "username": auth.email,
        "password": auth.password,
        "audience": AUTH0_AUDIENCE,
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "realm": "Username-Password-Authentication",
        "scope": "openid profile email"
    }

    response = requests.post(f"https://{AUTH0_DOMAIN}/oauth/token", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=response.json())
    return response.json()

@router.post("/register")
def register_user(auth: AuthRequest):
    token_res = requests.post(f"https://{AUTH0_DOMAIN}/oauth/token", json={
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    })

    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail=token_res.json())
    
    mgmt_token = token_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {mgmt_token}"}
    user_data = {
        "email": auth.email,
        "password": auth.password,
        "connection": "Username-Password-Authentication"
    }

    res = requests.post(f"https://{AUTH0_DOMAIN}/api/v2/users", json=user_data, headers=headers)
    if res.status_code != 201:
        raise HTTPException(status_code=400, detail=res.json())
    return {"message": "User created successfully."}
