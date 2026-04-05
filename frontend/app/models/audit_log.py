from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False)
    risk_score = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    reasons = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    claim = relationship("Claim", back_populates="audit_logs")
