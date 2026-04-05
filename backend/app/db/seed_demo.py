import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.claim import Claim, ClaimStatus
from app.models.audit_log import AuditLog
from app.models.system_config import SystemConfig

async def seed_demo_data():
    """
    Seeds the database with 3 defined archetype scenarios and system configuration.
    """
    print("--- 🚀 Seeding Advanced Archetype Demo Data ---")
    
    # 1. Initialize Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncSessionLocal()
    try:
        # 1.5 Seed System Config
        max_config = await db.execute(select(SystemConfig).filter(SystemConfig.id == "MAX_CREDIBLE_AMOUNT"))
        if not max_config.scalars().first():
            db.add(SystemConfig(id="MAX_CREDIBLE_AMOUNT", value=50000.0, description="Maximum amount for automatic approval"))
            await db.commit()
            print("Seeded default MAX_CREDIBLE_AMOUNT: 50,000")
        # 2. Reset existing demo names
        demo_emails = ["niranjan@guidewire.com", "rahul@guidewire.com", "kavya@guidewire.com", "demo.user@guidewire.com"]
        for email in demo_emails:
            res = await db.execute(select(Customer.id).where(Customer.email == email))
            ids = res.scalars().all()
            if ids:
                # 1. Fetch related Claim IDs first to resolve foreign key constraints iteratively
                claim_res = await db.execute(select(Claim.id).where(Claim.customer_id.in_(ids)))
                claim_ids = claim_res.scalars().all()
                if claim_ids:
                    await db.execute(delete(AuditLog).where(AuditLog.claim_id.in_(claim_ids)))
                await db.execute(delete(Claim).where(Claim.customer_id.in_(ids)))
                await db.execute(delete(Policy).where(Policy.customer_id.in_(ids)))
                await db.execute(delete(Customer).where(Customer.id.in_(ids)))
        await db.commit()

        # 3. Archetype 1: Niranjan (Target: APPROVE) - Stable, Safe, Veteran
        niranjan = Customer(name="Niranjan", email="niranjan@guidewire.com", age=45, region_density=1)
        db.add(niranjan)
        await db.flush()
        
        pol1 = Policy(
            customer_id=niranjan.id, policy_type="Premium Auto", vehicle_age=2, ncap_rating=5,
            start_date=datetime.utcnow() - timedelta(days=3650), # 10 years ago
            end_date=datetime.utcnow() + timedelta(days=365)
        )
        db.add(pol1)
        
        # 4. Archetype 2: Rahul (Target: INVESTIGATE) - New, Young, Low Safety
        rahul = Customer(name="Rahul", email="rahul@guidewire.com", age=20, region_density=2)
        db.add(rahul)
        await db.flush()
        
        pol2 = Policy(
            customer_id=rahul.id, policy_type="Basic Auto", vehicle_age=8, ncap_rating=2,
            start_date=datetime.utcnow() - timedelta(days=10), # 10 days ago (Window Alert)
            end_date=datetime.utcnow() + timedelta(days=355)
        )
        db.add(pol2)
        
        # 5. Archetype 3: Kavya (Target: REJECT) - High Density, High Severity, History
        kavya = Customer(name="Kavya", email="kavya@guidewire.com", age=30, region_density=4)
        db.add(kavya)
        await db.flush()
        
        pol3 = Policy(
            customer_id=kavya.id, policy_type="Standard Auto", vehicle_age=5, ncap_rating=3,
            start_date=datetime.utcnow() - timedelta(days=500),
            end_date=datetime.utcnow() + timedelta(days=230)
        )
        db.add(pol3)
        await db.flush()
        
        # Create suspicious historical claims for Kavya
        db.add_all([
            Claim(customer_id=kavya.id, policy_id=pol3.id, claim_amount=100.0, claim_date=datetime.utcnow()-timedelta(days=30), status=ClaimStatus.APPROVED, incident_severity="minor damage"),
            Claim(customer_id=kavya.id, policy_id=pol3.id, claim_amount=150.0, claim_date=datetime.utcnow()-timedelta(days=20), status=ClaimStatus.APPROVED, incident_severity="minor damage"),
            Claim(customer_id=kavya.id, policy_id=pol3.id, claim_amount=120.0, claim_date=datetime.utcnow()-timedelta(days=10), status=ClaimStatus.APPROVED, incident_severity="minor damage"),
        ])
        
        await db.commit()
        
        print("\n--- ✅ Advanced Archetypes Seeded Successfully ---")
        print(f"1. Niranjan [ID: {niranjan.id}] -> Policy [ID: {pol1.id}] (Safe)")
        print(f"2. Rahul    [ID: {rahul.id}] -> Policy [ID: {pol2.id}] (New/Rookie)")
        print(f"3. Kavya    [ID: {kavya.id}] -> Policy [ID: {pol3.id}] (High Risk Urban)")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"--- ❌ Seeding Failed: {e} ---")
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
