-- ============================================================================
-- LAKEWOOD FAMILY DENTAL CARE
-- PRODUCTION-GRADE POSTGRESQL DATABASE SCHEMA (DDL)
-- ============================================================================

-- Enable UUID extension for robust distributed identifier generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas to separate clinical/operational concerns from web marketing data
CREATE SCHEMA IF NOT EXISTS clinical;
CREATE SCHEMA IF NOT EXISTS web;
CREATE SCHEMA IF NOT EXISTS system;

-- ============================================================================
-- CUSTOM DOMAINS AND ENUMS
-- ============================================================================

-- Email validation domain
CREATE DOMAIN system.email_address AS VARCHAR(255)
CHECK (VALUE ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$');

-- Phone number domain (international format)
CREATE DOMAIN system.phone_number AS VARCHAR(30)
CHECK (VALUE ~* '^\+?[1-9]\d{1,14}$' OR VALUE ~* '^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$');

-- Enums
CREATE TYPE clinical.appointment_status AS ENUM (
    'PENDING', 
    'CONFIRMED', 
    'CANCELLED', 
    'COMPLETED',
    'NO_SHOW'
);

CREATE TYPE system.user_role AS ENUM (
    'SUPER_ADMIN', 
    'FRONT_DESK', 
    'DOCTOR', 
    'MARKETING'
);

CREATE TYPE web.inquiry_status AS ENUM (
    'NEW', 
    'CONTACTED', 
    'CONVERTED', 
    'ARCHIVED'
);

CREATE TYPE web.subscription_status AS ENUM (
    'ACTIVE', 
    'UNSUBSCRIBED', 
    'BOUNCED'
);

-- ============================================================================
-- CLINICAL & OPERATIONAL TABLES
-- ============================================================================

-- 1. TREATMENT CATEGORIES TABLE
CREATE TABLE web.treatment_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    icon VARCHAR(50) NOT NULL, -- FontAwesome/Custom Icon indicator
    image_url VARCHAR(255),
    seo_title VARCHAR(150),
    seo_description VARCHAR(255),
    seo_keywords VARCHAR(255),
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 2. DOCTORS TABLE
CREATE TABLE clinical.doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    specialization VARCHAR(100) NOT NULL,
    experience_years INT NOT NULL CHECK (experience_years >= 0),
    bio TEXT NOT NULL,
    profile_image_url VARCHAR(255),
    certifications TEXT[] NOT NULL DEFAULT '{}',
    social_linkedin VARCHAR(255),
    social_twitter VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 3. DOCTOR WEEKLY SCHEDULE TEMPLATE TABLE
CREATE TABLE clinical.doctor_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES clinical.doctors(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0 = Sunday, 6 = Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT check_time_slot CHECK (start_time < end_time),
    CONSTRAINT unique_doctor_day_time UNIQUE (doctor_id, day_of_week, start_time, end_time)
);

-- 4. APPOINTMENTS TABLE
CREATE TABLE clinical.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_name VARCHAR(150) NOT NULL,
    patient_email system.email_address NOT NULL,
    patient_phone system.phone_number NOT NULL,
    treatment_category_id UUID REFERENCES web.treatment_categories(id) ON DELETE SET NULL,
    doctor_id UUID REFERENCES clinical.doctors(id) ON DELETE RESTRICT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status clinical.appointment_status DEFAULT 'PENDING' NOT NULL,
    is_ppo_insurance BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Ensure no double booking: a doctor cannot be booked at the exact same date and time twice
    CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time),
    CONSTRAINT check_future_date CHECK (appointment_date >= CURRENT_DATE)
);

-- ============================================================================
-- WEBSITE SYSTEM & MARKETING TABLES
-- ============================================================================

-- 5. CONTACT LEADS TABLE
CREATE TABLE web.contact_leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    email system.email_address NOT NULL,
    phone system.phone_number,
    message TEXT NOT NULL,
    inquiry_type VARCHAR(50) NOT NULL, -- e.g., 'Insurance Query', 'General Info'
    lead_source VARCHAR(100) DEFAULT 'Direct Website Search', -- e.g., 'Google Ad', 'Local Pack'
    status web.inquiry_status DEFAULT 'NEW' NOT NULL,
    notes TEXT, -- Admin follow up comments
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 6. TESTIMONIALS TABLE
CREATE TABLE web.testimonials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_name VARCHAR(100) NOT NULL,
    review_text TEXT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    avatar_url VARCHAR(255),
    treatment_category_id UUID REFERENCES web.treatment_categories(id) ON DELETE SET NULL,
    is_featured BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified_google BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- BLOG SYSTEM TABLES
-- ============================================================================

-- 7. BLOG CATEGORIES
CREATE TABLE web.blog_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 8. BLOG TAGS
CREATE TABLE web.blog_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 9. BLOG POSTS
CREATE TABLE web.blog_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    excerpt VARCHAR(255),
    featured_image_url VARCHAR(255),
    author_id UUID NOT NULL, -- Links to system.admin_users
    category_id UUID REFERENCES web.blog_categories(id) ON DELETE SET NULL,
    seo_title VARCHAR(150),
    seo_description VARCHAR(255),
    is_published BOOLEAN DEFAULT FALSE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 10. BLOG POSTS TO TAGS JOIN TABLE
CREATE TABLE web.blog_post_tags (
    post_id UUID REFERENCES web.blog_posts(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES web.blog_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

-- ============================================================================
-- ADMINISTRATIVE USERS
-- ============================================================================

-- 11. ADMIN USERS TABLE
CREATE TABLE system.admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email system.email_address NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Hashed using Argon2id/bcrypt
    role system.user_role DEFAULT 'FRONT_DESK' NOT NULL,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Foreign key linking Author on blog post to Admin Users
ALTER TABLE web.blog_posts 
ADD CONSTRAINT fk_blog_author 
FOREIGN KEY (author_id) REFERENCES system.admin_users(id);

-- ============================================================================
-- AUDITING & AUXILIARY TABLES
-- ============================================================================

-- 12. NEWSLETTER SUBSCRIBERS TABLE
CREATE TABLE web.newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email system.email_address NOT NULL UNIQUE,
    status web.subscription_status DEFAULT 'ACTIVE' NOT NULL,
    ip_address VARCHAR(45), -- Track subscriber source for spam prevention
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    unsubscribed_at TIMESTAMP WITH TIME ZONE
);

-- 13. AI CHATBOT CONVERSATIONS LOG
CREATE TABLE system.chatbot_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_fingerprint VARCHAR(100), -- Browser fingerprint to associate messages
    user_email system.email_address, -- Optional email if context gathered
    user_phone system.phone_number, -- Optional phone if booking requested
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE system.chatbot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES system.chatbot_sessions(id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('USER', 'ASSISTANT')),
    message_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 14. PERFORMANCE & MARKETING ANALYTICS TRACKING
CREATE TABLE web.analytics_events (
    id BIGSERIAL PRIMARY KEY,
    session_token VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- e.g., 'PAGE_VISIT', 'BUTTON_CLICK', 'CONVERSION_BOOKING'
    element_id VARCHAR(100), -- HTML unique id tracked
    page_url VARCHAR(255) NOT NULL,
    referrer_url VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    traffic_medium VARCHAR(50), -- organic, cpc, social, direct
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- PERFORMANCE OPTIMIZATIONS (INDEXES)
-- ============================================================================

-- Speed up appointment availability checks & reports
CREATE INDEX idx_appointments_date_time ON clinical.appointments(appointment_date, appointment_time);
CREATE INDEX idx_appointments_doctor ON clinical.appointments(doctor_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_appointments_status ON clinical.appointments(status) WHERE deleted_at IS NULL;

-- Speed up search on website treatments & blogs
CREATE INDEX idx_treatment_categories_slug ON web.treatment_categories(slug);
CREATE INDEX idx_doctors_slug ON clinical.doctors(slug);
CREATE INDEX idx_blog_posts_slug ON web.blog_posts(slug) WHERE is_published = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_blog_posts_published ON web.blog_posts(published_at DESC) WHERE is_published = TRUE;

-- CRM Lead dashboard filters
CREATE INDEX idx_contact_leads_status ON web.contact_leads(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_contact_leads_created ON web.contact_leads(created_at DESC);

-- Analytics range querying
CREATE INDEX idx_analytics_event_type ON web.analytics_events(event_type, created_at DESC);
CREATE INDEX idx_analytics_session ON web.analytics_events(session_token);

-- Chatbot session mapping
CREATE INDEX idx_chatbot_session_ref ON system.chatbot_messages(session_id);

-- ============================================================================
-- DATABASE TRIGGERS FOR TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION system.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Register updated_at triggers on dynamic content tables
CREATE TRIGGER update_treatment_categories_modtime BEFORE UPDATE ON web.treatment_categories FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_doctors_modtime BEFORE UPDATE ON clinical.doctors FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_appointments_modtime BEFORE UPDATE ON clinical.appointments FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_contact_leads_modtime BEFORE UPDATE ON web.contact_leads FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_testimonials_modtime BEFORE UPDATE ON web.testimonials FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_blog_posts_modtime BEFORE UPDATE ON web.blog_posts FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
CREATE TRIGGER update_admin_users_modtime BEFORE UPDATE ON system.admin_users FOR EACH ROW EXECUTE PROCEDURE system.update_modified_column();
