from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.db.session import get_db
from app.models.system_config import SystemConfig

router = APIRouter()

class ConfigUpdate(BaseModel):
    value: float

@router.get("/config/{config_id}")
async def get_config(config_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemConfig).filter(SystemConfig.id == config_id))
    config = result.scalars().first()
    if not config:
        # Return a sensible default if not found in DB yet
        if config_id == "MAX_CREDIBLE_AMOUNT":
            return {"id": config_id, "value": 50000.0}
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.put("/config/{config_id}")
async def update_config(config_id: str, config_in: ConfigUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemConfig).filter(SystemConfig.id == config_id))
    config = result.scalars().first()
    
    if not config:
        config = SystemConfig(id=config_id, value=config_in.value, description="System setting")
        db.add(config)
    else:
        config.value = config_in.value
        
    await db.commit()
    await db.refresh(config)
    return config
