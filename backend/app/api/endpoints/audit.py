from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import io
import csv

from app.schemas.audit import AuditLogResponse
from app.models.audit_log import AuditLog
from app.models.claim import Claim
from app.models.customer import Customer
from app.db.session import get_db

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/export/{customer_id}")
async def export_audit_history(customer_id: int, db: AsyncSession = Depends(get_db)):
    """
    Export a full CSV audit history for a specific customer as transaction evidence.
    """
    # Join AuditLog with Claim to filter by customer_id
    result = await db.execute(
        select(AuditLog)
        .join(Claim)
        .filter(Claim.customer_id == customer_id)
        .options(joinedload(AuditLog.claim)) # Eager load the claim data
        .order_by(AuditLog.created_at.desc())
    )
    logs = result.scalars().all()

    if not logs:
        raise HTTPException(status_code=404, detail="No audit history found for this customer.")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Audit ID", "Claim ID", "Date", "Amount", 
        "Risk Score", "Decision", "Reasons"
    ])
    
    # Rows
    for log in logs:
        writer.writerow([
            log.id,
            log.claim_id,
            log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            f"{log.claim.claim_amount:.2f}",
            f"{log.risk_score:.4f}",
            log.decision,
            " | ".join(log.reasons) if isinstance(log.reasons, list) else log.reasons
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_history_cust_{customer_id}.csv"
        }
    )

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
