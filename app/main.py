from fastapi import FastAPI
<<<<<<< HEAD
from fastapi.middleware.cors import CORSMiddleware
=======
>>>>>>> 7689bc54eb680a43842f663490cbbb7a72dcb83b
from app.api.api import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API for the Insurance Claim Risk Decision Engine"
)

<<<<<<< HEAD
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

=======
>>>>>>> 7689bc54eb680a43842f663490cbbb7a72dcb83b
# Includes all API endpoints
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for Swagger UI."}
