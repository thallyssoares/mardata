
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import upload, chat, auth, notebooks
from .lib.redis_client import get_redis_pool, close_redis_pool

app = FastAPI(
    title="MarData API",
    description="API for the MarData platform, providing data analysis as a service.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    """Initialize Redis pool on startup."""
    await get_redis_pool()

@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis pool on shutdown."""
    await close_redis_pool()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Include the routers
app.include_router(upload.router, prefix="/api", tags=["Data Upload & Analysis"])
app.include_router(chat.router, prefix="/api", tags=["Interactive Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["Notebooks"])

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "MarData API is running"}
