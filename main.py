import os
from urllib.parse import quote

from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from calculator_backend import database, models
from calculator_backend.routers import auth, calculator
from calculator_backend.utils.jwt_handler import create_access_token

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

app = FastAPI(title="Calculator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY or "change-me",
)

models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth.router)
app.include_router(calculator.router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


def _validate_google_env() -> None:
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in .env",
        )


@app.get("/", response_class=HTMLResponse)
def get_register():
    with open("frontend/register.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/login", response_class=HTMLResponse)
def get_login():
    with open("frontend/login.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/calculator", response_class=HTMLResponse)
def get_calculator():
    with open("frontend/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/auth/google/login")
async def google_login(request: Request):
    _validate_google_env()
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request):
    _validate_google_env()
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo") or await oauth.google.parse_id_token(
        request,
        token,
    )

    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400, detail="Unable to read Google user email")
    name = user_info.get("name", "Google User")
    return RedirectResponse(url=f"/calculator?username={name}")
    