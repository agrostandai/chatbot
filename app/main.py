from fastapi import FastAPI
from app.routes import main_router

app = FastAPI(
    title="WhatsApp AI Bot",
    description="FastAPI app to chat and detect crop diseases",
    version="1.0.0"
)

# Add a root endpoint for health checks
@app.get("/")
async def root():
    return {"message": "WhatsApp AI Bot is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(main_router)

# Only run this when called directly (not when imported)
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)