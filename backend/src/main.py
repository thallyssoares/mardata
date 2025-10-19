
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes import upload, chat, auth, notebooks

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

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # This is a generic exception handler to ensure CORS headers are added to all 500 error responses.
    return JSONResponse(
        status_code=500,
        content={"message": f"An internal server error occurred: {exc}"},
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': '*',
        }
    )


# Include the routers
app.include_router(upload.router, prefix="/api", tags=["Data Upload & Analysis"])
app.include_router(chat.router, prefix="/api", tags=["Interactive Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["Notebooks"])

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "MarData API is running"}
