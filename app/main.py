from fastapi import FastAPI
from app.routes import main_router

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

app = FastAPI(
    title="WhatsApp AI Bot",
    description="FastAPI app to chat and detect crop diseases",
    version="1.0.0"
)

app.include_router(main_router)
