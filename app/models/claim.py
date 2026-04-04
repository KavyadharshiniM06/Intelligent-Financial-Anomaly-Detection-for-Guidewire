import enum
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class ClaimStatus(str, enum.Enum):
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    INVESTIGATING = "Investigating"

class Claim(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    claim_amount = Column(Float, nullable=False)
    claim_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    payments = relationship("Payment", back_populates="claim")
    audit_logs = relationship("AuditLog", back_populates="claim")
