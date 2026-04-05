import asyncio
import sys
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.models.customer import Customer
from app.models.policy import Policy


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as session:
        existing_customer = await session.execute(
            select(Customer).where(Customer.email == "demo.customer@example.com")
        )
        customer = existing_customer.scalars().first()

        if not customer:
            customer = Customer(
                name="Demo Customer",
                email="demo.customer@example.com",
            )
            session.add(customer)
            await session.commit()
            await session.refresh(customer)

        existing_policy = await session.execute(
            select(Policy).where(Policy.customer_id == customer.id)
        )
        policy = existing_policy.scalars().first()

        if not policy:
            policy = Policy(
                customer_id=customer.id,
                policy_type="Auto Comprehensive",
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow() + timedelta(days=335),
            )
            session.add(policy)
            await session.commit()
            await session.refresh(policy)

        print("--- Demo data ready ---")
        print(f"Customer ID: {customer.id}")
        print(f"Policy ID: {policy.id}")
        print("Use these values in the React frontend claim form.")

    await engine.dispose()


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_demo_data())
