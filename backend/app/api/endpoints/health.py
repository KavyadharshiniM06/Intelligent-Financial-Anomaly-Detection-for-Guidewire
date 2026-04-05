from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthResponse
from app.services.health_service import check_db_health
from app.db.session import get_db

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = await check_db_health(db)
    return HealthResponse(
        status="active",
        db_status="connected" if db_status else "disconnected",
        message="Decision Engine backend is running properly."
    )
