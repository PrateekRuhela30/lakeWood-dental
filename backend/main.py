# ============================================================================
# LAKEWOOD FAMILY DENTAL CARE
# FASTAPI PRODUCTION BACKEND CONTROLLER & REST API
# ============================================================================

import os
from datetime import date, time, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

# Import our SQLAlchemy models
from models import Base, TreatmentCategory, Doctor, Appointment, ContactLead, NewsletterSubscriber, ChatbotSession, ChatbotMessage, AnalyticsEvent

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:secure_pass_2026@localhost:5433/lakewood_dental")

# Create Async Engine for low-latency asynchronous connections
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_size=20, max_overflow=10)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI(
    title="Lakewood Dental Care API",
    description="High-performance backend API powering appointments, lead collection, AI chatbot sessions, and clinic dashboards.",
    version="1.0.0"
)

# Enable CORS for frontend deployment validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to fetch database sessions per request
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# ============================================================================
# PYDANTIC VALIDATION SCHEMAS
# ============================================================================

class TreatmentSchema(BaseModel):
    id: UUID
    title: str
    slug: str
    description: str
    icon: str
    image_url: Optional[str]
    is_featured: bool

    class Config:
        from_attributes = True

class DoctorSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    specialization: str
    bio: str
    profile_image_url: Optional[str]
    certifications: List[str]

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=150, examples=["Sarah Mitchell"])
    patient_email: EmailStr = Field(..., examples=["sarah@example.com"])
    patient_phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$|^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$")
    treatment_category_id: UUID
    doctor_id: UUID
    appointment_date: date
    appointment_time: time
    is_ppo_insurance: bool = False
    notes: Optional[str] = None

class AppointmentSchema(BaseModel):
    id: UUID
    patient_name: str
    appointment_date: date
    appointment_time: time
    status: str

    class Config:
        from_attributes = True

class ContactLeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = None
    message: str = Field(..., min_length=10)
    inquiry_type: str = Field(..., examples=["Insurance Claims", "Veneers Pricing", "General Inquiry"])
    lead_source: Optional[str] = "Direct Website Search"

class NewsletterCreate(BaseModel):
    email: EmailStr
    ip_address: Optional[str] = None

class ChatbotMessageCreate(BaseModel):
    session_id: Optional[UUID] = None
    user_fingerprint: Optional[str] = None
    sender: str = Field(..., pattern="^(USER|ASSISTANT)$")
    message_text: str

class AnalyticsEventCreate(BaseModel):
    session_token: str
    event_type: str
    element_id: Optional[str] = None
    page_url: str
    referrer_url: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    traffic_medium: Optional[str] = None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/treatments", response_model=List[TreatmentSchema])
async def list_treatments(db: AsyncSession = Depends(get_db)):
    """Fetch all active treatment categories for frontend mapping."""
    result = await db.execute(
        select(TreatmentCategory)
        .where(TreatmentCategory.deleted_at.is_(None))
        .order_by(TreatmentCategory.title)
    )
    return result.scalars().all()

@app.get("/api/doctors", response_model=List[DoctorSchema])
async def list_doctors(db: AsyncSession = Depends(get_db)):
    """Fetch all active doctor specialists and certifications."""
    result = await db.execute(
        select(Doctor).where(and_(Doctor.is_active == True, Doctor.deleted_at.is_(None)))
    )
    return result.scalars().all()

@app.post("/api/appointments", response_model=AppointmentSchema, status_code=status.HTTP_201_CREATED)
async def create_appointment(payload: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    """
    Schedules an appointment.
    Implements database-level transaction checking to prevent double-booking.
    """
    if payload.appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule appointments in past dates."
        )

    # Check double booking in database
    existing_booking = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == payload.doctor_id,
                Appointment.appointment_date == payload.appointment_date,
                Appointment.appointment_time == payload.appointment_time,
                Appointment.deleted_at.is_(None),
                Appointment.status != "CANCELLED"
            )
        )
    )
    if existing_booking.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected doctor is already booked for this specific time slot. Please choose another date or time."
        )

    new_appt = Appointment(
        patient_name=payload.patient_name,
        patient_email=payload.patient_email,
        patient_phone=payload.patient_phone,
        treatment_category_id=payload.treatment_category_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        is_ppo_insurance=payload.is_ppo_insurance,
        notes=payload.notes,
        status="PENDING"
    )
    db.add(new_appt)
    try:
        await db.flush()
        return new_appt
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Double booking collision detected during transaction serialization. Please retry with a different slot."
        )

@app.post("/api/leads", status_code=status.HTTP_201_CREATED)
async def create_contact_lead(payload: ContactLeadCreate, db: AsyncSession = Depends(get_db)):
    """Submits contact form inquiry to lead database."""
    new_lead = ContactLead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        message=payload.message,
        inquiry_type=payload.inquiry_type,
        lead_source=payload.lead_source,
        status="NEW"
    )
    db.add(new_lead)
    return {"status": "success", "message": "Lead captured successfully"}

@app.post("/api/newsletter/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_newsletter(payload: NewsletterCreate, db: AsyncSession = Depends(get_db)):
    """Registers emails for patient newsletters."""
    # Check if subscriber already exists
    existing = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == payload.email)
    )
    if existing.scalars().first():
        return {"status": "success", "message": "Email already subscribed"}

    new_sub = NewsletterSubscriber(
        email=payload.email,
        ip_address=payload.ip_address,
        status="ACTIVE"
    )
    db.add(new_sub)
    return {"status": "success", "message": "Subscribed successfully"}

@app.post("/api/chat/message", status_code=status.HTTP_201_CREATED)
async def log_chatbot_message(payload: ChatbotMessageCreate, db: AsyncSession = Depends(get_db)):
    """Stores user questions and AI chatbot session transcripts."""
    session_id = payload.session_id
    
    # If no session ID is supplied, initialize a session
    if not session_id:
        new_session = ChatbotSession(user_fingerprint=payload.user_fingerprint)
        db.add(new_session)
        await db.flush()
        session_id = new_session.id
        
    new_msg = ChatbotMessage(
        session_id=session_id,
        sender=payload.sender,
        message_text=payload.message_text
    )
    db.add(new_msg)
    return {"status": "success", "session_id": session_id}

@app.post("/api/analytics/event", status_code=status.HTTP_200_OK)
async def log_analytics_event(payload: AnalyticsEventCreate, db: AsyncSession = Depends(get_db)):
    """Captures page views, conversions, and UI interaction clicks."""
    event = AnalyticsEvent(
        session_token=payload.session_token,
        event_type=payload.event_type,
        element_id=payload.element_id,
        page_url=payload.page_url,
        referrer_url=payload.referrer_url,
        ip_address=payload.ip_address,
        user_agent=payload.user_agent,
        traffic_medium=payload.traffic_medium
    )
    db.add(event)
    return {"status": "logged"}

# ============================================================================
# ADMIN CRM DASHBOARD SECURE METRICS
# ============================================================================

@app.get("/api/admin/dashboard/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns administrative operational summaries.
    Typically protected by OAuth2 JSON Web Tokens (JWT).
    """
    # Total appointments scheduled
    total_appts_query = await db.execute(select(func.count(Appointment.id)))
    total_appts = total_appts_query.scalar_one()

    # Total unconverted new leads
    new_leads_query = await db.execute(
        select(func.count(ContactLead.id)).where(ContactLead.status == "NEW")
    )
    new_leads = new_leads_query.scalar_one()

    # Total active newsletter subscribers
    subs_query = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(NewsletterSubscriber.status == "ACTIVE")
    )
    subs = subs_query.scalar_one()

    return {
        "status": "success",
        "data": {
            "total_appointments": total_appts,
            "new_leads_pending": new_leads,
            "active_newsletter_subscribers": subs
        }
    }
