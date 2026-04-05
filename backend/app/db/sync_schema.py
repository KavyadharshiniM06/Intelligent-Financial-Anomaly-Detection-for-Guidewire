import asyncio
from sqlalchemy import text
from app.db.session import engine

async def sync_existing_schema():
    """
    Safely adds missing columns required for the professional 12-feature demo
    to an existing Guidewire database.
    """
    print("--- 🔄 Synchronizing Professional Database Schema ---")
    
    statements = [
        # Customer Table Fixes
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS age INTEGER DEFAULT 35",
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS region_density INTEGER DEFAULT 1",
        
        # Policy Table Fixes
        "ALTER TABLE policies ADD COLUMN IF NOT EXISTS vehicle_age INTEGER DEFAULT 5",
        "ALTER TABLE policies ADD COLUMN IF NOT EXISTS ncap_rating INTEGER DEFAULT 4",
        
        # System Config Table Fixes
        """
        CREATE TABLE IF NOT EXISTS system_configs (
            id VARCHAR PRIMARY KEY,
            value FLOAT NOT NULL,
            description VARCHAR
        )
        """,
    ]
    
    async with engine.begin() as conn:
        try:
            for statement in statements:
                print(f"Executing: {statement}")
                await conn.execute(text(statement))
            print("\n--- ✅ Schema Synchronization Successful ---")
        except Exception as e:
            print(f"\n--- ❌ Schema Sync Failed: {e} ---")

if __name__ == "__main__":
    asyncio.run(sync_existing_schema())
