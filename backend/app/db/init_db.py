import asyncio
from app.db.session import engine
from app.models.base import Base

# We MUST import all models so that the metadata knows about them
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payment import Payment
from app.models.audit_log import AuditLog

async def init_models():
    """
    Initializes the database schema by creating all tables 
    defined in the SQLAlchemy models.
    """
    async with engine.begin() as conn:
        # Run the table creation logic
        # For small projects, this is a simple alternative to Alembic
        print("--- Connecting to database and creating tables ---")
        await conn.run_sync(Base.metadata.create_all)
        print("--- Database schema initialized successfully! ---")

if __name__ == "__main__":
    asyncio.run(init_models())
