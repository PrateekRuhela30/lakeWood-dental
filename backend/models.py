# ============================================================================
# LAKEWOOD FAMILY DENTAL CARE
# SQLALCHEMY PRODUCTION MODELS
# ============================================================================

import uuid
from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, Date, Time, 
    DateTime, ForeignKey, Table, Enum, BigInteger, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# Many-to-Many association table for blog posts and tags
blog_post_tags = Table(
    "blog_post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("web.blog_posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("web.blog_tags.id", ondelete="CASCADE"), primary_key=True),
    schema="web"
)

# 1. TREATMENT CATEGORY
class TreatmentCategory(Base):
    __tablename__ = "treatment_categories"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    seo_title: Mapped[Optional[str]] = mapped_column(String(150))
    seo_description: Mapped[Optional[str]] = mapped_column(String(255))
    seo_keywords: Mapped[Optional[str]] = mapped_column(String(255))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="treatment_category")
    testimonials: Mapped[List["Testimonial"]] = relationship(back_populates="treatment_category")


# 2. DOCTOR
class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = {"schema": "clinical"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, CheckConstraint("experience_years >= 0"), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(255))
    certifications: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    social_linkedin: Mapped[Optional[str]] = mapped_column(String(255))
    social_twitter: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="doctor")
    schedules: Mapped[List["DoctorSchedule"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")


# 3. DOCTOR WEEKLY SCHEDULE TEMPLATE
class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    __table_args__ = (
        UniqueConstraint("doctor_id", "day_of_week", "start_time", "end_time", name="unique_doctor_day_time"),
        CheckConstraint("start_time < end_time", name="check_time_slot"),
        {"schema": "clinical"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clinical.doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, CheckConstraint("day_of_week BETWEEN 0 AND 6"), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    doctor: Mapped["Doctor"] = relationship(back_populates="schedules")


# 4. APPOINTMENT
class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("doctor_id", "appointment_date", "appointment_time", name="unique_doctor_slot"),
        CheckConstraint("appointment_date >= CURRENT_DATE", name="check_future_date"),
        {"schema": "clinical"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_name: Mapped[str] = mapped_column(String(150), nullable=False)
    patient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    treatment_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("web.treatment_categories.id", ondelete="SET NULL"))
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clinical.doctors.id", ondelete="RESTRICT"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(Enum("PENDING", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW", name="appointment_status", inherit_schema=True), default="PENDING", nullable=False)
    is_ppo_insurance: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    treatment_category: Mapped[Optional["TreatmentCategory"]] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")


# 5. CONTACT LEADS
class ContactLead(Base):
    __tablename__ = "contact_leads"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    inquiry_type: Mapped[str] = mapped_column(String(50), nullable=False)
    lead_source: Mapped[Optional[str]] = mapped_column(String(100), default="Direct Website Search")
    status: Mapped[str] = mapped_column(Enum("NEW", "CONTACTED", "CONVERTED", "ARCHIVED", name="inquiry_status", inherit_schema=True), default="NEW", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


# 6. TESTIMONIALS
class Testimonial(Base):
    __tablename__ = "testimonials"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, CheckConstraint("rating BETWEEN 1 AND 5"), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    treatment_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("web.treatment_categories.id", ondelete="SET NULL"))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified_google: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    treatment_category: Mapped[Optional["TreatmentCategory"]] = relationship(back_populates="testimonials")


# 7. BLOG CATEGORY
class BlogCategory(Base):
    __tablename__ = "blog_categories"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="category")


# 8. BLOG TAG
class BlogTag(Base):
    __tablename__ = "blog_tags"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# 9. BLOG POST
class BlogPost(Base):
    __tablename__ = "blog_posts"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(String(255))
    featured_image_url: Mapped[Optional[str]] = mapped_column(String(255))
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("system.admin_users.id"), nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("web.blog_categories.id", ondelete="SET NULL"))
    seo_title: Mapped[Optional[str]] = mapped_column(String(150))
    seo_description: Mapped[Optional[str]] = mapped_column(String(255))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    category: Mapped[Optional["BlogCategory"]] = relationship(back_populates="blog_posts")
    author: Mapped["AdminUser"] = relationship(back_populates="blog_posts")
    tags: Mapped[List["BlogTag"]] = relationship(secondary=blog_post_tags)


# 10. ADMIN USER
class AdminUser(Base):
    __tablename__ = "admin_users"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("SUPER_ADMIN", "FRONT_DESK", "DOCTOR", "MARKETING", name="user_role", inherit_schema=True), default="FRONT_DESK", nullable=False)
    permissions: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    blog_posts: Mapped[List["BlogPost"]] = relationship(back_populates="author")


# 11. NEWSLETTER SUBSCRIBER
class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    __table_args__ = {"schema": "web"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(Enum("ACTIVE", "UNSUBSCRIBED", "BOUNCED", name="subscription_status", inherit_schema=True), default="ACTIVE", nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    subscribed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


# 12. CHATBOT SESSION
class ChatbotSession(Base):
    __tablename__ = "chatbot_sessions"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_fingerprint: Mapped[Optional[str]] = mapped_column(String(100))
    user_email: Mapped[Optional[str]] = mapped_column(String(255))
    user_phone: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    messages: Mapped[List["ChatbotMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")


# 13. CHATBOT MESSAGE
class ChatbotMessage(Base):
    __tablename__ = "chatbot_messages"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("system.chatbot_sessions.id", ondelete="CASCADE"), nullable=False)
    sender: Mapped[str] = mapped_column(String(20), CheckConstraint("sender IN ('USER', 'ASSISTANT')"), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["ChatbotSession"] = relationship(back_populates="messages")


# 14. ANALYTICS EVENT
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = {"schema": "web"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    element_id: Mapped[Optional[str]] = mapped_column(String(100))
    page_url: Mapped[str] = mapped_column(String(255), nullable=False)
    referrer_url: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    traffic_medium: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
