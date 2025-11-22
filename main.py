from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from calculator_backend import models,database
from calculator_backend.routers import auth, calculator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Calculator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=database.engine)



app.include_router(auth.router)
app.include_router(calculator.router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the HTML file
@app.get("/", response_class=HTMLResponse)
def get_register():
    with open("frontend/register.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.get("/login", response_class=HTMLResponse)
def get_login():
    with open("frontend/login.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.get("/calculator", response_class=HTMLResponse)
def get_calculator():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content
