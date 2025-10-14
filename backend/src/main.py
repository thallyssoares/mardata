
from fastapi import FastAPI
from .routes import upload, chat
from typing import Dict

# In-memory store for analysis sessions. 
# This will be imported by other modules to share state.
sessions: Dict[str, Dict] = {}

app = FastAPI(
    title="MarData API",
    description="API for the MarData platform, providing data analysis as a service.",
    version="0.1.0",
)

# Include the routers
app.include_router(upload.router, prefix="/api", tags=["Data Upload & Analysis"])
app.include_router(chat.router, prefix="/api", tags=["Interactive Chat"])

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "MarData API is running"}
