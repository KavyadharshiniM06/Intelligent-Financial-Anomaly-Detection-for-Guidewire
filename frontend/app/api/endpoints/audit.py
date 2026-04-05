from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.audit import AuditLogResponse
from app.models.audit_log import AuditLog
from app.db.session import get_db

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/{claim_id}", response_model=AuditLogResponse)
async def get_audit_log(claim_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve the audit log for a specific claim by ID.
    """
    result = await db.execute(select(AuditLog).filter(AuditLog.claim_id == claim_id))
    audit_log = result.scalars().first()
    
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found for this claim.")
        
    return audit_log
