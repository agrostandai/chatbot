from fastapi import FastAPI
from app.routes import main_router

app = FastAPI(
    title="WhatsApp AI Bot",
    description="FastAPI app to chat and detect crop diseases",
    version="1.0.0"
)

# Health check endpoint for Render
@app.get("/")
async def root():
    return {"message": "WhatsApp AI Bot is running!", "status": "healthy"}

app.include_router(main_router)
