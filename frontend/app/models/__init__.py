from app.models.base import Base
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.claim import Claim, ClaimStatus
from app.models.payment import Payment
from app.models.audit_log import AuditLog

# Expose models for easier imports and for Alembic migrations
__all__ = [
    "Base", 
    "Customer", 
    "Policy", 
    "Claim", 
    "ClaimStatus", 
    "Payment", 
    "AuditLog"
]
