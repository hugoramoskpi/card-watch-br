from fastapi import FastAPI
from src.db.database import create_tables
from src.api.routes import router

app = FastAPI(title="Card Watch BR")
app.include_router(router)

@app.on_event("startup")
def startup():
    create_tables()
