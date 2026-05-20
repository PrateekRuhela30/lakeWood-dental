import asyncio
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from main import create_appointment, AppointmentCreate
from models import Base

async def test():
    DATABASE_URL = "postgresql+asyncpg://postgres:secure_pass_2026@localhost:5433/lakewood_dental"
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    future_date = datetime.datetime.now() + datetime.timedelta(days=5)
    
    payload = AppointmentCreate(
        patient_name="Autobook Tester",
        patient_email="autobook.tester@example.com",
        patient_phone="2148230099",
        treatment_category_id="22222222-2222-2222-2222-222222222222",
        doctor_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        appointment_date=future_date.date(),
        appointment_time=datetime.time(10, 0),
        is_ppo_insurance=True,
        notes="Insurance plan coverage selected: Yes"
    )
    
    async with async_session() as db:
        try:
            print("Calling create_appointment...")
            result = await create_appointment(payload, db)
            print("Result:", result)
            await db.commit()
        except Exception as e:
            print(f"Exception caught: {type(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
