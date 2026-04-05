from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Policy(Base):
    __tablename__ = 'policies'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    policy_type = Column(String, nullable=False)
    vehicle_age = Column(Integer, nullable=False, default=5)
    ncap_rating = Column(Integer, nullable=False, default=4)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")
