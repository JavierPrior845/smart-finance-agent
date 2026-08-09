from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

app = FastAPI(
    title="Smart Finance Agent API",
    description="Production-grade Personal Finance API featuring Hexagonal Architecture and AI Categorization.",
    version="0.1.0",
)

# Configure CORS for Web Application frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.infrastructure.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": app.version,
    }

