import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from . import models, database, routes, auth

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Create default admin user
db = database.SessionLocal()
try:
    auth.create_default_admin(db)
except Exception as e:
    print(f"[AVISO] Error creating admin user: {e}")
finally:
    db.close()

app = FastAPI(title="Agente Financeiro API", description="API para App Financeiro Colombiano", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

# Mount frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
