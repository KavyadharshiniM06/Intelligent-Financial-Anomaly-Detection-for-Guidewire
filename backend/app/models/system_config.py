from sqlalchemy import Column, String, Float
from app.models.base import Base

class SystemConfig(Base):
    """
    Stores dynamic application configuration settings.
    """
    __tablename__ = "system_configs"

    id = Column(String, primary_key=True)  # Setting Key
    value = Column(Float, nullable=False) # Setting Value
    description = Column(String, nullable=True) # Meaning of the setting
