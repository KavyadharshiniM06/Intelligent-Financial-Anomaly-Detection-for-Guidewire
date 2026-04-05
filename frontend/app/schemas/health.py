from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    db_status: str
    message: str
