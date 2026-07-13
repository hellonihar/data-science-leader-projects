import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.assignment import Assignment
from app.models.experiment import Experiment
from app.models.interaction import Interaction
from app.models.item import Item
from app.models.user import User


async def seed():
    async with async_session_factory() as session:
        existing = await session.execute(select(User).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded, skipping.")
            return

        print("Seeding database...")

        users = []
        for i in range(100):
            user = User(
                username=f"user_{i:03d}",
                email=f"user_{i:03d}@example.com",
            )
            session.add(user)
            users.append(user)
        await session.flush()

        categories = ["electronics", "books", "clothing", "home", "sports"]
        items = []
        for i in range(50):
            item = Item(
                name=f"Product {i:03d}",
                category=random.choice(categories),
                price=round(random.uniform(5.0, 200.0), 2),
            )
            session.add(item)
            items.append(item)
        await session.flush()

        experiment = Experiment(
            name="CF vs DL v1",
            description="Comparing collaborative filtering with deep learning recommendations",
            status="active",
            traffic_split=0.5,
            variant_a_label="collaborative_filtering",
            variant_b_label="deep_learning",
            start_date=datetime.now(timezone.utc) - timedelta(days=7),
        )
        session.add(experiment)
        await session.flush()

        rng = random.Random(42)
        interaction_types = ["impression", "impression", "impression", "click", "purchase"]
        for user in users:
            variant = "A" if rng.random() < 0.5 else "B"
            assignment = Assignment(
                user_id=user.id,
                experiment_id=experiment.id,
                variant=variant,
            )
            session.add(assignment)

            num_items = rng.randint(5, 15)
            sampled_items = rng.sample(items, min(num_items, len(items)))
            for item in sampled_items:
                int_type = rng.choice(interaction_types)
                revenue = None
                if int_type == "purchase":
                    revenue = round(item.price * rng.uniform(0.8, 1.2), 2)

                interaction = Interaction(
                    user_id=user.id,
                    item_id=item.id,
                    interaction_type=int_type,
                    experiment_id=experiment.id,
                    variant=variant,
                    revenue=revenue,
                    timestamp=datetime.now(timezone.utc) - timedelta(hours=rng.randint(0, 168)),
                )
                session.add(interaction)

        await session.commit()
        print("Seed complete: 100 users, 50 items, 1 active experiment, 1000+ interactions")


async def main():
    await seed()


if __name__ == "__main__":
    asyncio.run(main())
