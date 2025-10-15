
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import upload, chat
from .state import sessions

app = FastAPI(
    title="MarData API",
    description="API for the MarData platform, providing data analysis as a service.",
    version="0.1.0",
)

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

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "MarData API is running"}
