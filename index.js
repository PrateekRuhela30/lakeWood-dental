/* ==========================================================================
   PHOENIX-IntrusionX Redesign Project
   lakewood_redesign/index.js — Interactive Client Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initHeaderScroll();
    initMobileNav();
    initSmileSlider();
    initFaqAccordion();
    initAccessibilityKeyboard();
    // Country select auto-prepend
    const countrySelect = document.getElementById('countrySelect');
    const phoneInput = document.getElementById('patientPhone');
    if (countrySelect && phoneInput) {
        countrySelect.addEventListener('change', function() {
            // Only prepend if not already present
            let val = phoneInput.value.trim();
            // Remove any existing country code
            val = val.replace(/^\+?\d{1,4}/, '');
            phoneInput.value = this.value + val;
        });
        // On focus, if empty, prefill with country code
        phoneInput.addEventListener('focus', function() {
            if (!phoneInput.value.startsWith(countrySelect.value)) {
                phoneInput.value = countrySelect.value;
            }
        });
    }
});

/* ── 1. HEADER SCROLL & MOBILE NAV OVERLAY ───────────────────────────────── */
function initHeaderScroll() {
    const header = document.getElementById('header');
    if (!header) return;
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

function initMobileNav() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navBar = document.getElementById('navBar');
    
    if (mobileToggle && navBar) {
        mobileToggle.addEventListener('click', () => {
            const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
            mobileToggle.setAttribute('aria-expanded', !expanded);
            mobileToggle.classList.toggle('open');
            navBar.classList.toggle('open');
        });

        // Close when clicking nav link
        navBar.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileToggle.setAttribute('aria-expanded', 'false');
                mobileToggle.classList.remove('open');
                navBar.classList.remove('open');
            });
        });
    }
}

/* ── 2. INTERACTIVE SMILE BEFORE/AFTER SLIDER ────────────────────────────── */
function initSmileSlider() {
    const wrapper = document.getElementById('smileSliderWrapper');
    const afterPane = document.getElementById('afterPane');
    const handle = document.getElementById('sliderHandle');
    
    if (!wrapper || !afterPane || !handle) return;
    
    let isDragging = false;

    function setSliderPosition(x) {
        const rect = wrapper.getBoundingClientRect();
        let percentage = ((x - rect.left) / rect.width) * 100;
        
        // Boundaries checks
        if (percentage < 0) percentage = 0;
        if (percentage > 100) percentage = 100;
        
        afterPane.style.width = `${100 - percentage}%`;
        handle.style.left = `${percentage}%`;
    }

    // Pointer events for desktop & mobile
    wrapper.addEventListener('pointerdown', (e) => {
        isDragging = true;
        setSliderPosition(e.clientX);
        wrapper.setPointerCapture(e.pointerId);
    });

    wrapper.addEventListener('pointermove', (e) => {
        if (!isDragging) return;
        setSliderPosition(e.clientX);
    });

    wrapper.addEventListener('pointerup', () => {
        isDragging = false;
    });

    wrapper.addEventListener('pointercancel', () => {
        isDragging = false;
    });

    // Keyboard support for slider accessibility (Left/Right Arrows)
    wrapper.addEventListener('keydown', (e) => {
        let currentLeft = parseFloat(handle.style.left) || 50;
        if (e.key === 'ArrowLeft') {
            currentLeft = Math.max(0, currentLeft - 5);
            afterPane.style.width = `${100 - currentLeft}%`;
            handle.style.left = `${currentLeft}%`;
        } else if (e.key === 'ArrowRight') {
            currentLeft = Math.min(100, currentLeft + 5);
            afterPane.style.width = `${100 - currentLeft}%`;
            handle.style.left = `${currentLeft}%`;
        }
    });
}

/* ── 3. FAQ ACCORDION TRANSITIONS ────────────────────────────────────────── */
function toggleFaq(item) {
    const isActive = item.classList.contains('active');
    
    // Collapse other items
    document.querySelectorAll('.faq-item').forEach(el => {
        el.classList.remove('active');
    });
    
    if (!isActive) {
        item.classList.add('active');
    }
}

function initFaqAccordion() {
    // Already set inline via onclick, but we can set initial closed state
    document.querySelectorAll('.faq-item').forEach(item => {
        if (item.classList.contains('active')) {
            item.classList.remove('active');
        }
    });
}

/* ── 4. APPOINTMENT BOOKING ACCESSIBILITY & ESCAPE KEY ───────────────────── */
function initAccessibilityKeyboard() {
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeBookingModal();
            closeServiceModal();
            // Close Chatbot panel
            const chatbotPanel = document.getElementById('chatbotPanel');
            if (chatbotPanel) chatbotPanel.classList.remove('open');
        }
    });
}

/* ── 5. MULTI-STEP BOOKING MODAL SYSTEM ──────────────────────────────────── */
const bookingModal = document.getElementById('bookingModalOverlay');
let currentStep = 1;
const totalSteps = 4;

const bookingData = {
    service: '',
    doctor: '',
    date: '',
    time: '',
    name: '',
    phone: '',
    email: '',
    insurance: ''
};

function openBookingModal() {
    bookingModal.classList.add('open');
    bookingModal.focus(); // Shift focus for screen readers
    document.body.style.overflow = 'hidden'; // Scroll lock
    resetBookingModal();
}

function closeBookingModal() {
    bookingModal.classList.remove('open');
    document.body.style.overflow = 'auto'; // Release scroll
}

function resetBookingModal() {
    currentStep = 1;
    updateStepView();
    // Reset inputs & values
    bookingData.service = '';
    bookingData.doctor = '';
    bookingData.date = '';
    bookingData.time = '';
    
    document.querySelectorAll('.booking-opt-card').forEach(card => card.classList.remove('selected'));
    
    const dateInput = document.getElementById('bookingDate');
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateInput.min = `${yyyy}-${mm}-${dd}`;
    dateInput.value = '';
    
    document.getElementById('timeSlotsGrid').innerHTML = '<span class="no-date-msg">Please pick a date first to display slots.</span>';
    document.getElementById('bookingFinalForm').reset();
}

function selectBookingOption(type, value, element) {
    // Update active class on siblings
    const siblings = element.parentNode.children;
    for (let sibling of siblings) {
        sibling.classList.remove('selected');
    }
    element.classList.add('selected');
    
    bookingData[type] = value;
    
    // Automatically skip to next step for fast UX
    setTimeout(() => {
        navigateBookingStep(1);
    }, 300);
}

function navigateBookingStep(direction) {
    // Validate current step before moving forward
    if (direction === 1) {
        if (currentStep === 1 && !bookingData.service) {
            alert('Please select a dental service to proceed.');
            return;
        }
        if (currentStep === 2 && !bookingData.doctor) {
            alert('Please select a dental specialist.');
            return;
        }
        if (currentStep === 3) {
            if (!bookingData.date) {
                alert('Please select an appointment date.');
                return;
            }
            if (!bookingData.time) {
                alert('Please select an available hour slot.');
                return;
            }
        }
    }
    
    currentStep += direction;
    if (currentStep < 1) currentStep = 1;
    if (currentStep > totalSteps) currentStep = totalSteps;
    
    updateStepView();
}

function updateStepView() {
    // Toggle active pane
    document.querySelectorAll('.booking-step-pane').forEach((pane, idx) => {
        if (idx + 1 === currentStep) {
            pane.classList.add('pane-active');
        } else {
            pane.classList.remove('pane-active');
        }
    });

    // Update Progress Indicator
    const progressFill = document.getElementById('bookingProgressFill');
    const percentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
    progressFill.style.width = `${percentage}%`;

    document.querySelectorAll('.progress-step').forEach((step, idx) => {
        if (idx + 1 < currentStep) {
            step.className = 'progress-step completed';
        } else if (idx + 1 === currentStep) {
            step.className = 'progress-step active';
        } else {
            step.className = 'progress-step';
        }
    });

    // Toggle Back/Next buttons visibility
    const prevBtn = document.getElementById('prevStepBtn');
    const nextBtn = document.getElementById('nextStepBtn');
    
    if (currentStep === 1) {
        prevBtn.style.display = 'none';
    } else {
        prevBtn.style.display = 'block';
    }

    if (currentStep === totalSteps) {
        nextBtn.style.display = 'none';
        // Fill Summary details for patient
        document.getElementById('summaryService').innerText = bookingData.service;
        document.getElementById('summaryDoc').innerText = bookingData.doctor;
        document.getElementById('summaryDateTime').innerText = `${bookingData.date} at ${bookingData.time}`;
    } else {
        nextBtn.style.display = 'block';
    }
}

// Generate interactive slots dynamically
function generateTimeSlots() {
    const dateInput = document.getElementById('bookingDate');
    
    // Set minimum date to today if not already set
    if (!dateInput.min) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dateInput.min = `${yyyy}-${mm}-${dd}`;
    }

    const dateVal = dateInput.value;
    bookingData.date = dateVal;
    
    const slotsGrid = document.getElementById('timeSlotsGrid');
    if (!dateVal) {
        slotsGrid.innerHTML = '<span class="no-date-msg">Please pick a date first to display slots.</span>';
        return;
    }
    
    const slots = ['9:00 AM', '10:00 AM', '11:00 AM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'];
    slotsGrid.innerHTML = '';
    
    slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'time-slot-btn';
        btn.innerText = slot;
        btn.onclick = () => {
            // Remove selected class from others
            slotsGrid.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            bookingData.time = slot;
            // Instantly skip to details screen
            setTimeout(() => {
                navigateBookingStep(1);
            }, 300);
        };
        slotsGrid.appendChild(btn);
    });
}

function submitBooking(event) {
    event.preventDefault();
    
    bookingData.name = document.getElementById('patientName').value;
    const countryCode = document.getElementById('countrySelect').value;
    let phoneVal = document.getElementById('patientPhone').value.trim();
    // Remove any leading zeros or pluses from phoneVal
    phoneVal = phoneVal.replace(/^0+/, '').replace(/^\+/, '');
    bookingData.phone = countryCode + phoneVal;
    bookingData.email = document.getElementById('patientEmail').value;
    bookingData.insurance = document.getElementById('patientInsurance').value;
    
    // Map service string name to seeded PostgreSQL UUID
    const serviceIds = {
        'Preventive Dentistry': '11111111-1111-1111-1111-111111111111',
        'Cosmetic Dentistry': '22222222-2222-2222-2222-222222222222',
        'Restorative Dentistry': '33333333-3333-3333-3333-333333333333',
        'Invisalign Treatment': '44444444-4444-4444-4444-444444444444',
        'Dental Implants': '55555555-5555-5555-5555-555555555555',
        'Emergency Dental Care': '66666666-6666-6666-6666-666666666666'
    };
    
    // Map doctor string name to seeded PostgreSQL UUID
    const doctorIds = {
        'Dr. Reid Slaughter': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        'Dr. Austin Farmer': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'First Available Dentist': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    };

    const serviceId = serviceIds[bookingData.service] || '11111111-1111-1111-1111-111111111111';
    const doctorId = doctorIds[bookingData.doctor] || 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';

    // Helper to convert '9:00 AM' / '1:00 PM' slots into valid 24h '09:00:00' format
    function convertTimeTo24h(timeStr) {
        if (!timeStr) return '09:00:00';
        const parts = timeStr.split(' ');
        const time = parts[0];
        const modifier = parts[1];
        let [hours, minutes] = time.split(':');
        if (hours === '12') {
            hours = '00';
        }
        if (modifier === 'PM') {
            hours = parseInt(hours, 10) + 12;
        }
        return `${String(hours).padStart(2, '0')}:${minutes}:00`;
    }

    const timeFormatted = convertTimeTo24h(bookingData.time);

    // Build the request payload
    const payload = {
        patient_name: bookingData.name,
        patient_email: bookingData.email,
        patient_phone: bookingData.phone,
        treatment_category_id: serviceId,
        doctor_id: doctorId,
        appointment_date: bookingData.date,
        appointment_time: timeFormatted,
        is_ppo_insurance: bookingData.insurance === 'Yes',
        notes: `Insurance plan coverage selected: ${bookingData.insurance}`
    };

    // UI Loading state
    const submitButton = event.target.querySelector('button[type="submit"]') || document.getElementById('nextStepBtn');
    const originalText = submitButton ? submitButton.innerText : 'Confirm Appointment';
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerText = 'Securing Slot...';
    }

    // Set this to your production backend domain (e.g. 'https://lakewood-backend.onrender.com') when deploying.
    // For local development, use 'http://127.0.0.1:8001'
    const BACKEND_URL = 'https://lakewood-backend.onrender.com';

    // Call live FastAPI server
    fetch(`${BACKEND_URL}/api/appointments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                let errorMsg = err.detail || 'Failed to book slot';
                if (typeof errorMsg === 'object') {
                    errorMsg = JSON.stringify(errorMsg);
                }
                throw new Error(errorMsg);
            });
        }
        return response.json();
    })
    .then(data => {
        // Transition to Success pane
        document.querySelectorAll('.booking-step-pane').forEach(pane => pane.classList.remove('pane-active'));
        document.getElementById('bookPaneSuccess').classList.add('pane-active');
        
        // Hide footer controls in success
        document.getElementById('prevStepBtn').style.display = 'none';
        if (document.getElementById('nextStepBtn')) document.getElementById('nextStepBtn').style.display = 'none';
        document.getElementById('bookingProgressFill').style.width = '100%';
        document.querySelectorAll('.progress-step').forEach(step => {
            step.className = 'progress-step completed';
        });
        
        document.getElementById('sentEmail').innerText = bookingData.email;
    })
    .catch(error => {
        alert(`Booking Error: ${error.message}`);
    })
    .finally(() => {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerText = originalText;
        }
    });
}

/* ── 6. TREATMENT SERVICE DESCRIPTION MODALS ──────────────────────────────── */
const serviceModal = document.getElementById('serviceModalOverlay');
const serviceContent = document.getElementById('serviceModalContent');

const serviceDetails = {
    preventive: {
        icon: '🧹',
        title: 'Preventative & Cleaning',
        body: 'Biannual cleanings prevent bacterial buildup and decay. Our treatment includes:<br><ul><li>Ultrasonic stain removal and scaling</li><li>Full digital mouth decay mapping</li><li>Fluoride protective varnish</li><li>Certified periodontal cleaning</li></ul><br><strong>Typical Consult Duration:</strong> 45 minutes.<br><strong>Acceptable Financing:</strong> 100% PPO coverage.'
    },
    restorative: {
        icon: '🦷',
        title: 'Restorative Dental Works',
        body: 'Address structural damages or cavities instantly with color matching composite fillings. Treatments include:<br><ul><li>Decay removal & composite fillings</li><li>Root canal procedures</li><li>Single porcelain crowns & bridges</li><li>Full mouth metal-free restorations</li></ul><br><strong>Typical Consult Duration:</strong> 60 - 90 minutes.<br><strong>Acceptable Financing:</strong> Insurance accepted & CareCredit supported.'
    },
    cosmetic: {
        icon: '✨',
        title: 'Cosmetic Veneers',
        body: 'Transform tooth shape, spacing, or deep stains using our ultra-thin porcelain or composite shells. Sculpting details include:<br><ul><li>Premium stain-resistant porcelain</li><li>Custom thickness smile design</li><li>No-prep composite options</li><li>Permanent symmetry alignment</li></ul><br><strong>Typical Consult Duration:</strong> 2 visits.<br><strong>Acceptable Financing:</strong> CareCredit interest-free options available.'
    },
    aligners: {
        icon: '🌀',
        title: 'Invisalign® Clear Aligners',
        body: 'Achieve perfectly straight dental structures with removable, hygienic Invisalign® aligners. Clear corrections details include:<br><ul><li>Precise virtual 3D treatment planning</li><li>Discreet, comfortable transparent shells</li><li>Easy teeth cleaning access</li><li>Bite alignment correction</li></ul><br><strong>Typical Treatment Duration:</strong> 6 - 15 months.<br><strong>Acceptable Financing:</strong> Orthodontic insurance & low monthly payments.'
    }
};

function openServiceModal(type) {
    const details = serviceDetails[type];
    if (!details) return;
    
    serviceContent.innerHTML = `
        <div class="serv-details-header">
            <span class="serv-details-icon" aria-hidden="true">${details.icon}</span>
            <h3 class="serv-details-name" id="serviceTitle">${details.title}</h3>
        </div>
        <div class="serv-details-body">
            <p>${details.body}</p>
        </div>
        <button class="btn btn-primary w-full" onclick="closeServiceModal(); openBookingModal();">Book Treatment Consult</button>
    `;
    
    serviceModal.classList.add('open');
    serviceModal.focus();
    document.body.style.overflow = 'hidden';
}

function closeServiceModal() {
    serviceModal.classList.remove('open');
    document.body.style.overflow = 'auto';
}

/* ── 7. FLOATING DYNAMIC DENTAL CHATBOT AI ASSISTANT ─────────────────────── */
const chatbotPanel = document.getElementById('chatbotPanel');
const chatBody = document.getElementById('chatBody');

function toggleChatbot() {
    chatbotPanel.classList.toggle('open');
}

function sendQuickMessage(text) {
    addChatMessage(text, 'user');
    
    // Simulate thinking delay
    showBotTyping();
    setTimeout(() => {
        removeBotTyping();
        const reply = getBotResponse(text);
        addChatMessage(reply, 'assistant');
    }, 800);
}

function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;
    
    addChatMessage(text, 'user');
    input.value = '';
    
    showBotTyping();
    setTimeout(() => {
        removeBotTyping();
        const reply = getBotResponse(text);
        addChatMessage(reply, 'assistant');
    }, 800);
}

function addChatMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = `chat-msg msg-${sender}`;
    msg.innerHTML = text;
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
}

function showBotTyping() {
    const typing = document.createElement('div');
    typing.className = 'chat-msg msg-assistant bot-typing';
    typing.id = 'botTypingMsg';
    typing.innerText = 'typing...';
    chatBody.appendChild(typing);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function removeBotTyping() {
    const el = document.getElementById('botTypingMsg');
    if (el) el.remove();
}

function getBotResponse(query) {
    const cleanQuery = query.toLowerCase();
    
    if (cleanQuery.includes('insurance') || cleanQuery.includes('aetna') || cleanQuery.includes('ppo')) {
        return 'We accept most major dental PPO insurance plans, including Aetna, Blue Cross Blue Shield, Delta Dental, MetLife, and Cigna. Our front desk handles all paperwork for you! Would you like to <a href="#" onclick="toggleChatbot(); openBookingModal();" style="text-decoration: underline; font-weight: bold; color: #fb8b24;">book a consult</a>?';
    }
    if (cleanQuery.includes('carecredit') || cleanQuery.includes('payment') || cleanQuery.includes('financing')) {
        return 'Yes, we partner directly with CareCredit to offer interest-free monthly financing for all clinical procedures, including cosmetic veneers and Invisalign®. We also provide custom in-house installment plans!';
    }
    if (cleanQuery.includes('hour') || cleanQuery.includes('open') || cleanQuery.includes('saturday')) {
        return 'Lakewood Family Dental Care is open <strong>Monday through Friday, from 9:00 AM to 5:00 PM</strong>. We are closed on Saturdays and Sundays. For urgent dental pain, we hold emergency priority blocks every day!';
    }
    if (cleanQuery.includes('address') || cleanQuery.includes('location') || cleanQuery.includes('where')) {
        return 'Our premium clinic is located in the heart of Lakewood at <strong>6329 Oram Street, Dallas, TX 75214</strong>, near Richmond Ave. There is plenty of free patient parking directly in front of the clinic.';
    }
    if (cleanQuery.includes('invisalign') || cleanQuery.includes('aligners') || cleanQuery.includes('straight')) {
        return 'Yes! Dr. Austin Farmer is a certified Invisalign® provider. We offer comprehensive transparent alignment plans. Would you like to <a href="#" onclick="toggleChatbot(); openBookingModal();" style="text-decoration: underline; font-weight: bold; color: #fb8b24;">book a free aligner consult</a>?';
    }
    if (cleanQuery.includes('veneers') || cleanQuery.includes('cosmetic')) {
        return 'Porcelain and composite veneers are a key specialty of Dr. Reid Slaughter! We can completely redesign your smile in just 2 quick clinical visits. Let\'s schedule a cosmetic analysis.';
    }
    if (cleanQuery.includes('phone') || cleanQuery.includes('call') || cleanQuery.includes('number')) {
        return 'You can call our clinic front desk directly at <a href="tel:2148231638" style="font-weight: bold; color: #fb8b24;">(214) 823-1638</a>. We would love to chat and answer any questions!';
    }
    if (cleanQuery.includes('blog') || cleanQuery.includes('articles')) {
        return 'Explore our Lakewood Smile Blog directly on the page! We cover premium topics such as selecting Dallas Invisalign providers and veneers investments. Scroll down to review them!';
    }
    if (cleanQuery.includes('about') || cleanQuery.includes('clinic')) {
        return 'We have been serving Dallas for over 18 years, having helped over 5,000 happy patient smile goals. Dr. Reid Slaughter and Dr. Austin Farmer put comfort safety first!';
    }
    
    // Default reply
    return 'I would love to help you with that! At Lakewood Family Dental Care, we provide complete cosmetic veneers, Invisalign®, and general family checkups. The fastest way to secure a slot is to <a href="#" onclick="toggleChatbot(); openBookingModal();" style="text-decoration: underline; font-weight: bold; color: #fb8b24;">book an appointment online</a> or call us at (214) 823-1638.';
}
