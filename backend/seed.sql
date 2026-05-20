-- ============================================================================
-- LAKEWOOD FAMILY DENTAL CARE
-- PRODUCTION MOCK SEED DATA FOR TESTING & INGESTION
-- ============================================================================

-- 1. SEED TREATMENT CATEGORIES
-- Store primary UUID keys for foreign key references in session variables
DO $$
DECLARE
    cat_prev_id UUID := '11111111-1111-1111-1111-111111111111';
    cat_cosm_id UUID := '22222222-2222-2222-2222-222222222222';
    cat_rest_id UUID := '33333333-3333-3333-3333-333333333333';
    cat_invi_id UUID := '44444444-4444-4444-4444-444444444444';
    cat_impl_id UUID := '55555555-5555-5555-5555-555555555555';
    cat_emer_id UUID := '66666666-6666-6666-6666-666666666666';

    doc_slaughter_id UUID := 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
    doc_farmer_id    UUID := 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';

    admin_id UUID := 'dddddddd-dddd-dddd-dddd-dddddddddddd';
BEGIN

    -- Clear tables
    DELETE FROM clinical.appointments;
    DELETE FROM clinical.doctor_schedules;
    DELETE FROM clinical.doctors;
    DELETE FROM web.testimonials;
    DELETE FROM web.blog_posts;
    DELETE FROM web.blog_categories;
    DELETE FROM web.blog_tags;
    DELETE FROM web.treatment_categories;
    DELETE FROM system.admin_users;

    -- SEED treatment_categories
    INSERT INTO web.treatment_categories (id, title, slug, description, icon, image_url, seo_title, seo_description, is_featured) VALUES
    (cat_prev_id, 'Preventive Dentistry', 'preventive-dentistry', 'Routine cleanings, exams, and preventive care for long-term oral health.', '🧹', '/assets/images/treatments/preventive.jpg', 'Preventive Dentistry & Cleanings Dallas TX | Lakewood Family', 'Top-rated dental exams, cleanings, and digital X-rays in Lakewood Dallas. Book your family cleaning session today.', true),
    (cat_cosm_id, 'Cosmetic Dentistry', 'cosmetic-dentistry', 'Enhance your smile with veneers, whitening, and smile makeovers.', '✨', '/assets/images/treatments/cosmetic.jpg', 'Cosmetic Smile Veneers & Teeth Whitening Dallas TX', 'Transform your smile with porcelain veneers, professional Zoom whitening, and dental bonding. Experienced cosmetic dentists in Lakewood.', true),
    (cat_rest_id, 'Restorative Dentistry', 'restorative-dentistry', 'Restore damaged teeth with crowns, fillings, and advanced treatments.', '🦷', '/assets/images/treatments/restorative.jpg', 'Restorative Tooth Crowns, Bridges & Dental Fillings Dallas', 'Expert restorative dental care in Dallas, TX. Clean composite fillings, porcelain crowns, and root canals in a comfortable boutique clinic.', true),
    (cat_invi_id, 'Invisalign Treatment', 'invisalign-treatment', 'Straighten your teeth discreetly with modern clear aligners.', '🌀', '/assets/images/treatments/invisalign.jpg', 'Invisalign® Clear Aligners Orthodontics Lakewood Dallas', 'Discreet orthodontics with custom Invisalign clear aligners in Dallas. Book a digital smile scan consultation with Dr. Farmer.', true),
    (cat_impl_id, 'Dental Implants', 'dental-implants', 'Permanent tooth replacement solutions with natural aesthetics.', '🔩', '/assets/images/treatments/implants.jpg', 'Dental Implant Tooth Replacement Surgery Dallas TX', 'Restore your bite with single and multi-tooth premium dental implants. High durability and natural look. Book implant checkup.', false),
    (cat_emer_id, 'Emergency Dental Care', 'emergency-dental-care', 'Immediate treatment for pain, broken teeth, and urgent dental issues.', '🚨', '/assets/images/treatments/emergency.jpg', '24/7 Emergency Dentist Dallas TX | Call Urgent Dental Team', 'Immediate treatment for broken teeth, lost crowns, severe tooth pain, and oral bleeding in Lakewood Dallas.', false);

    -- SEED doctors
    INSERT INTO clinical.doctors (id, first_name, last_name, slug, specialization, experience_years, bio, profile_image_url, certifications, social_linkedin, is_active) VALUES
    (doc_slaughter_id, 'Reid', 'Slaughter', 'dr-reid-slaughter', 'General & Implant Dentistry', 14, 'Dr. Reid Slaughter has over a decade of experience providing dental care. He is dedicated to cosmetic restorations, surgical implant placements, and utilizing state-of-the-art tools.', '/assets/images/doctors/slaughter.jpg', ARRAY['DDS - Baylor College of Dentistry', 'Fellow of International Congress of Oral Implantologists (ICOI)'], 'https://www.linkedin.com/in/reid-slaughter-dds', true),
    (doc_farmer_id, 'Austin', 'Farmer', 'dr-austin-farmer', 'Invisalign® & Family Dentistry', 8, 'Dr. Austin Farmer specializes in clear aligner therapeutics, preventive orthodontics, and restorative pediatric dentistry, ensuring patients of all ages leave with a bright smile.', '/assets/images/doctors/farmer.jpg', ARRAY['DDS - Texas A&M College of Dentistry', 'Invisalign® Certified Diamond Provider'], 'https://www.linkedin.com/in/austin-farmer-dds', true);

    -- SEED doctor_schedules (Mon-Fri, 9am - 5pm, 1 hour slots)
    FOR day IN 1..5 LOOP
        -- Dr. Slaughter
        INSERT INTO clinical.doctor_schedules (doctor_id, day_of_week, start_time, end_time) VALUES
        (doc_slaughter_id, day, '09:00:00', '13:00:00'),
        (doc_slaughter_id, day, '14:00:00', '17:00:00');
        
        -- Dr. Farmer
        INSERT INTO clinical.doctor_schedules (doctor_id, day_of_week, start_time, end_time) VALUES
        (doc_farmer_id, day, '09:00:00', '12:00:00'),
        (doc_farmer_id, day, '13:00:00', '17:00:00');
    END LOOP;

    -- SEED admin_users (Password: Hashed representation of 'SecureAdminPass2026!')
    INSERT INTO system.admin_users (id, username, email, password_hash, role, permissions, is_active) VALUES
    (admin_id, 'admin_coordinator', 'scheduler@lakewoodfamilydental.com', '$2b$12$Z0HwG8/u1.0gZ57Z2Q2RGeGqWvM9Z5G85Z85Z85Z85Z85Z85Z85Z.', 'SUPER_ADMIN', ARRAY['*'], true);

    -- SEED testimonials
    INSERT INTO web.testimonials (patient_name, review_text, rating, avatar_url, treatment_category_id, is_featured, is_verified_google) VALUES
    ('Sarah Mitchell', 'Absolutely loved my dental experience here. Dr. Slaughter was so thorough and explained every detail of my cosmetic veneers. My smile looks stunning!', 5, '/assets/images/patients/sarah.jpg', cat_cosm_id, true, true),
    ('David Chen', 'I was terrified of getting a dental implant, but the team here made it painless. The technology they use is unbelievable. Outstanding results.', 5, '/assets/images/patients/david.jpg', cat_impl_id, true, true),
    ('Emily Johnson', 'My teen daughter is halfway through her Invisalign treatment with Dr. Farmer. The scans were quick, the appointments are fast, and her teeth look straight already!', 5, '/assets/images/patients/emily.jpg', cat_invi_id, true, true);

    -- SEED blog categories & tags
    INSERT INTO web.blog_categories (id, name, slug) VALUES
    ('00000000-0000-0000-0000-000000000001', 'Oral Hygiene', 'oral-hygiene'),
    ('00000000-0000-0000-0000-000000000002', 'Cosmetic Trends', 'cosmetic-trends');

    INSERT INTO web.blog_tags (id, name, slug) VALUES
    ('00000000-0000-0000-0000-000000000003', 'Whitening', 'whitening'),
    ('00000000-0000-0000-0000-000000000004', 'Invisalign', 'invisalign');

    -- SEED blog_posts
    INSERT INTO web.blog_posts (title, slug, content, excerpt, author_id, category_id, is_published, published_at) VALUES
    ('Top 5 Dental Habits to Prevent Cavities', 'top-5-habits-prevent-cavities', 'This is a complete clinical guide detailing the optimal brushing techniques, fluoride benefits, and diet guidelines to protect your enamel...', 'Simple daily habits to protect your teeth.', admin_id, '00000000-0000-0000-0000-000000000001', true, NOW()),
    ('Why Invisalign is the Preferred Choice for Adults', 'why-invisalign-preferred-choice-adults', 'Gone are the days of bulky metal braces. Modern clear aligners offer custom force dynamics and removable convenience...', 'Why clear aligners are ideal for busy professionals.', admin_id, '00000000-0000-0000-0000-000000000002', true, NOW());

    -- SEED appointments (Prevent double-booking collision demo, slot dates in future)
    INSERT INTO clinical.appointments (patient_name, patient_email, patient_phone, treatment_category_id, doctor_id, appointment_date, appointment_time, status, notes) VALUES
    ('Alice Vance', 'alice@gmail.com', '(214) 823-1111', cat_prev_id, doc_slaughter_id, CURRENT_DATE + INTERVAL '1 day', '09:00:00', 'CONFIRMED', 'Regular cleanings & checkup'),
    ('Bob Harris', 'bob@gmail.com', '(214) 823-2222', cat_invi_id, doc_farmer_id, CURRENT_DATE + INTERVAL '1 day', '10:00:00', 'PENDING', 'Check Invisalign tracking');

END $$;
