from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def check_db_health(db: AsyncSession) -> bool:
    try:
        # Execute a simple query to determine if DB is healthy
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"--- Database connection error: {e} ---")
        return False
