from fastapi import APIRouter
from app.api.endpoints import health, claims, audit, admin

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(claims.router, prefix="/claims", tags=["claims"])
api_router.include_router(audit.router)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
