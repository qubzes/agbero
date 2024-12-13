import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as chat_router
from app.settings import Settings

settings = Settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend application for Agbero",
    debug=settings.DEBUG,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Health Check"])
async def health_check():
    """Health check endpoint to verify API status"""
    response = requests.get(
        "https://official-joke-api.appspot.com/jokes/programming/random"
    )
    data = response.json()[0]
    joke = {"question": data["setup"], "answer": data["punchline"]}

    return {
        "status": "healthy",
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "swagger": f"{settings.API_PREFIX}/docs",
        "redoc": f"{settings.API_PREFIX}/redoc",
        "joke": joke,
    }
