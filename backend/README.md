# Lakewood Family Dental Care Database & Backend Architecture

This directory contains the production-grade PostgreSQL database schema, ORM declarations, mock seeds, and API routes designed for high-concurrency patient scheduling, CRM lead tracking, AI chatbot sessions, and clinic analytics.

---

## 📂 Project Directory Structure

```text
lakewood_redesign/backend/
├── schema.sql           # Raw PostgreSQL DDL (Schemas, Enums, Tables, Triggers, Constraints)
├── schema.prisma        # Prisma ORM Schema for Node.js / Full-stack frameworks
├── models.py            # SQLAlchemy Declarative Models (Python backend)
├── main.py              # FastAPI REST API Backend Controller with validation & transactions
├── seed.sql             # Comprehensive SQL seed data matching the frontend layout
└── README.md            # This detailed database architecture guide
```

---

## 📊 Database Relationships (Entity-Relationship Diagram)

```mermaid
erDiagram
    %% Schemas demarcation
    %% Clinical Schema
    clinical_doctors ||--o{ clinical_doctor_schedules : "weekly template"
    clinical_doctors ||--o{ clinical_appointments : "assigned to"
    clinical_appointments }o--|| web_treatment_categories : "selects"
    
    %% Web Schema
    web_testimonials }o--|| web_treatment_categories : "relates to"
    web_blog_posts }o--|| web_blog_categories : "categorized by"
    web_blog_posts }o--|{ web_blog_tags : "tagged with"
    system_admin_users ||--o{ web_blog_posts : "authors"
    
    %% Chatbot Schema
    system_chatbot_sessions ||--o{ system_chatbot_messages : "contains"
    
    clinical_doctors {
        uuid id PK
        varchar first_name
        varchar last_name
        varchar slug UK
        varchar specialization
        int experience_years
        text bio
        varchar profile_image_url
        array certifications
        varchar social_linkedin
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    clinical_doctor_schedules {
        uuid id PK
        uuid doctor_id FK
        int day_of_week
        time start_time
        time end_time
        boolean is_available
    }

    clinical_appointments {
        uuid id PK
        varchar patient_name
        varchar patient_email
        varchar patient_phone
        uuid treatment_category_id FK
        uuid doctor_id FK
        date appointment_date
        time appointment_time
        enum status
        boolean is_ppo_insurance
        text notes
        timestamp created_at
        timestamp updated_at
    }

    web_treatment_categories {
        uuid id PK
        varchar title UK
        varchar slug UK
        text description
        varchar icon
        varchar image_url
        varchar seo_title
        varchar seo_description
        boolean is_featured
        timestamp created_at
        timestamp updated_at
    }

    web_testimonials {
        uuid id PK
        varchar patient_name
        text review_text
        int rating
        varchar avatar_url
        uuid treatment_category_id FK
        boolean is_featured
        boolean is_verified_google
    }

    web_blog_posts {
        uuid id PK
        varchar title
        varchar slug UK
        text content
        varchar excerpt
        uuid author_id FK
        uuid category_id FK
        boolean is_published
        timestamp published_at
    }

    web_blog_categories {
        uuid id PK
        varchar name UK
        varchar slug UK
    }

    web_blog_tags {
        uuid id PK
        varchar name UK
        varchar slug UK
    }

    system_admin_users {
        uuid id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum role
        array permissions
        boolean is_active
    }

    system_chatbot_sessions {
        uuid id PK
        varchar user_fingerprint
        varchar user_email
        varchar user_phone
        timestamp created_at
    }

    system_chatbot_messages {
        uuid id PK
        uuid session_id FK
        varchar sender
        text message_text
        timestamp created_at
    }
```

---

## ⚡ Concurrency & Double-Booking Mitigation

To prevent race conditions where two patients attempt to book the same doctor at the same hour, the database implements two layers of isolation:

1. **Unique Index Constraints**: 
   A composite constraint is registered on the appointments table:
   ```sql
   CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
   ```
2. **Transaction Locking**:
   In high-concurrency environments, select-then-insert checks are vulnerable to timing race conditions. The FastAPI backend employs a database-level transaction checking system. When utilizing SQLAlchemy or raw SQL, queries search for conflicting records within a serialized lock block:
   ```python
   # Sample SQL executing under SERIALIZABLE transaction isolation:
   SELECT 1 FROM clinical.appointments 
   WHERE doctor_id = :doc_id 
     AND appointment_date = :app_date 
     AND appointment_time = :app_time 
     AND status != 'CANCELLED' 
     AND deleted_at IS NULL;
   ```

---

## 📈 Indexing & Query Optimizations

To maintain low latency (<50ms) as the database scales, the following indexes are declared:

*   **`idx_appointments_date_time`**: Covers `(appointment_date, appointment_time)`. Crucial for rendering the active schedule grid in the UI.
*   **`idx_appointments_doctor`**: A filtered index (`WHERE deleted_at IS NULL`) targeting queries displaying schedules specific to a single doctor.
*   **`idx_blog_posts_published`**: Covers `(published_at DESC) WHERE is_published = TRUE`. Optimizes front-end blog pagination and retrieval speed.
*   **`idx_contact_leads_status`**: Filtered index (`WHERE deleted_at IS NULL`) powering the administrative CRM panel to show new leads efficiently.

---

## 🔄 Migration Setup

### Option A: Node.js / Prisma ORM
If you are deploying a fullstack JavaScript dashboard:
1. Ensure a PostgreSQL connection string is set in your `.env` file:
   ```env
   DATABASE_URL="postgresql://postgres:secure_pass@localhost:5432/lakewood_dental?schema=public"
   ```
2. Run initial prisma migration setup to sync database schemas:
   ```bash
   npx prisma migrate dev --name init_database
   ```
3. Run the prisma seed file or standard ingestion commands to populate treatment values.

### Option B: Python / Alembic (SQLAlchemy)
If deploying via FastAPI:
1. Initialize Alembic in the backend directory:
   ```bash
   alembic init alembic
   ```
2. In `alembic/env.py`, import `Base` from `models.py` and set:
   ```python
   from models import Base
   target_metadata = Base.metadata
   ```
3. Generate the migration script:
   ```bash
   alembic revision --autogenerate -m "create_dental_tables"
   ```
4. Run migration:
   ```bash
   alembic upgrade head
   ```

---

## 🔒 Security Best Practices

1. **SQL Injection Prevention**: 
   All queries use SQLAlchemy's parameter binding or Prisma's parametrized query model. Dynamic string formatting (`f"SELECT ... {input}"`) is strictly prohibited.
2. **Password Safety**: 
   Administrative passwords are encrypted using **Argon2id** (minimum `m=65536, t=3, p=4` configuration) or **bcrypt** with a work factor of `12`.
3. **Soft Deletes**: 
   Soft delete timestamps (`deleted_at`) prevent accidental data loss and maintain historical integrity of clinical appointments.
