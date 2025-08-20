from fastapi import FastAPI
from app.routes import main_router

app = FastAPI(
    title="WhatsApp AI Bot",
    description="FastAPI app to chat and detect crop diseases",
    version="1.0.0"
)

app.include_router(main_router)
