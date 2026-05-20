import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_
from models import Appointment
from datetime import date, time

DATABASE_URL = "postgresql+asyncpg://postgres:secure_pass_2026@localhost:5433/lakewood_dental"

async def test_db():
    print("Testing DB connection...")
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            print("Executing query...")
            existing_booking = await db.execute(
                select(Appointment).where(
                    and_(
                        Appointment.appointment_date == date.today(),
                        Appointment.deleted_at.is_(None),
                        Appointment.status != "CANCELLED"
                    )
                )
            )
            print("Query successful!")
            print(existing_booking.scalars().all())
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
