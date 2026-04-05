from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API for the Insurance Claim Risk Decision Engine"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo, allow all. Can be restricted to localhost:3000 later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includes all API endpoints
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for Swagger UI."}
