/**
 * PaperTrail Authentication Pages Enhanced Interactions
 * Phases 1-3: Complete interactive experience for Login & Register
 */

// ============================================================================
// PHASE 1: QUICK WINS - Core Interactions
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎓 PaperTrail Auth Enhancements Loaded');
    
    // Initialize all Phase 1 features
    initPasswordToggles();
    initFormLoadingStates();
    initEnhancedErrorHandling();
    initInputValidation();
    
    // Initialize Phase 2 features if on register page
    if (document.getElementById('registerForm')) {
        initRegistrationFeatures();
    }
    
    // Initialize Phase 3 features
    initPhase3Features();
});

// ============================================================================
// Password Toggle Functionality (Enhanced)
// ============================================================================
function initPasswordToggles() {
    console.log('🔐 Initializing password toggles...');
    const passwordToggles = document.querySelectorAll('.password-toggle');
    console.log('Found toggle buttons:', passwordToggles.length);
    
    passwordToggles.forEach((toggle, index) => {
        console.log(`Processing toggle ${index + 1}...`);
        
        // Find the password field in the same parent wrapper
        const passwordWrapper = toggle.closest('.password-wrapper');
        if (!passwordWrapper) {
            console.log(`Toggle ${index + 1}: No password-wrapper found`);
            return;
        }
        
        // Find any input in the wrapper (Django might add classes/IDs)
        const passwordField = passwordWrapper.querySelector('input');
        
        if (!passwordField) {
            console.log(`Toggle ${index + 1}: No password field found`);
            return;
        }
        
        console.log(`Toggle ${index + 1}: Found password field`, passwordField);
        console.log(`Toggle ${index + 1}: Field type is: ${passwordField.type}`);
        console.log(`Toggle ${index + 1}: Field name is: ${passwordField.name}`);
        
        // Create img element for SVG icon
        const icon = document.createElement('img');
        icon.src = '/static/svgs/basil--eye-outline.svg';
        icon.alt = 'Show password';
        icon.style.width = '20px';
        icon.style.height = '20px';
        
        // Clear existing content and add SVG
        toggle.innerHTML = '';
        toggle.appendChild(icon);
        
        // Show/hide toggle based on input
        passwordField.addEventListener('input', function() {
            if (this.value.length > 0) {
                toggle.style.display = 'flex';
                console.log('Toggle shown');
            } else {
                toggle.style.display = 'none';
                console.log('Toggle hidden');
            }
        });
        
        // Toggle visibility
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🖱️ Toggle clicked!');
            console.log('Current type BEFORE:', passwordField.type);
            
            const currentType = passwordField.type;
            const newType = currentType === 'password' ? 'text' : 'password';
            
            // Change the type
            passwordField.type = newType;
            
            console.log('Current type AFTER:', passwordField.type);
            console.log(`Password type changed: ${currentType} → ${newType}`);
            
            // Change SVG icon with smooth transition
            icon.style.opacity = '0';
            setTimeout(() => {
                if (newType === 'text') {
                    icon.src = '/static/svgs/basil--eye-solid.svg';
                    icon.alt = 'Hide password';
                    console.log('Icon changed to SOLID (hide)');
                } else {
                    icon.src = '/static/svgs/basil--eye-outline.svg';
                    icon.alt = 'Show password';
                    console.log('Icon changed to OUTLINE (show)');
                }
                icon.style.opacity = '1';
            }, 150);
        });
        
        // Check on load
        if (passwordField.value.length > 0) {
            toggle.style.display = 'flex';
            console.log('Toggle shown on load');
        }
        
        console.log(`Toggle ${index + 1}: Setup complete ✓`);
    });
    
    console.log('✅ Password toggle initialization complete');
}

// ============================================================================
// Form Loading States
// ============================================================================
function initFormLoadingStates() {
    const forms = document.querySelectorAll('#loginForm, #registerForm');
    
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        const originalHtml = submitBtn.innerHTML;
        
        form.addEventListener('submit', function(e) {
            // Check if form is valid first
            const requiredFields = form.querySelectorAll('input[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('shake-horizontal');
                    setTimeout(() => field.classList.remove('shake-horizontal'), 500);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            const loadingText = form.id === 'loginForm' ? 'Signing you in...' : 'Creating your account...';
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${loadingText}
            `;
        });
    });
}

// ============================================================================
// Enhanced Error Handling
// ============================================================================
function initEnhancedErrorHandling() {
    const alerts = document.querySelectorAll('.alert-danger');
    
    alerts.forEach(alert => {
        // Add shake animation
        alert.classList.add('shake-horizontal');
        
        // Auto-dismiss after 8 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 8000);
    });
}

// ============================================================================
// Real-time Input Validation (Phase 1 Basic)
// ============================================================================
function initInputValidation() {
    // Email/Username validation for login
    const usernameField = document.querySelector('input[name="username"]');
    if (usernameField) {
        usernameField.addEventListener('blur', function() {
            const value = this.value.trim();
            if (value.includes('@') || /^\d{2}-\d{4}-\d{3}$/.test(value)) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else if (value.length > 3) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    }
}

// ============================================================================
// PHASE 2: ENGAGEMENT BOOSTERS - Advanced Features
// ============================================================================

function initRegistrationFeatures() {
    initFormProgressTracker();
    initRealTimeValidation();
    initPasswordStrength();
    initPasswordMatch();
    initAnimatedCounter();
}

// ============================================================================
// Form Progress Tracker
// ============================================================================
function initFormProgressTracker() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    // Create progress bar HTML
    const progressHTML = `
        <div class="signup-progress mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="small text-muted">
                    <i class="fas fa-clock me-1"></i>About 2 minutes
                </span>
                <span class="small fw-bold text-success">
                    <i class="fas fa-shield-check me-1"></i>Secure & Private
                </span>
            </div>
            <div class="progress" style="height: 4px;">
                <div class="progress-bar bg-warning" role="progressbar" 
                     style="width: 0%; transition: width 0.4s ease;" 
                     id="formProgress"></div>
            </div>
        </div>
    `;
    
    // Insert before form
    form.insertAdjacentHTML('beforebegin', progressHTML);
    
    const progressBar = document.getElementById('formProgress');
    const formInputs = form.querySelectorAll('input:not([type="hidden"])');
    
    function updateProgress() {
        const filledFields = Array.from(formInputs).filter(inp => inp.value.trim().length > 0).length;
        const progress = (filledFields / formInputs.length) * 100;
        progressBar.style.width = progress + '%';
        
        // Change color based on progress
        progressBar.className = 'progress-bar';
        if (progress === 100) {
            progressBar.classList.add('bg-success');
        } else if (progress > 50) {
            progressBar.classList.add('bg-info');
        } else {
            progressBar.classList.add('bg-warning');
        }
    }
    
    formInputs.forEach(input => {
        input.addEventListener('input', updateProgress);
    });
}

// ============================================================================
// Real-time Field Validation
// ============================================================================
function initRealTimeValidation() {
    // University Email Validation
    const univEmailField = document.querySelector('input[name="univ_email"]');
    if (univEmailField) {
        const feedback = createFeedbackElement();
        univEmailField.parentElement.appendChild(feedback);
        
        univEmailField.addEventListener('input', function() {
            const value = this.value.toLowerCase().trim();
            
            if (value.endsWith('@cit.edu') && value.length > 8) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
                feedback.innerHTML = `
                    <span class="text-success">
                        <i class="fas fa-check-circle me-1"></i>Perfect! This email works.
                    </span>
                `;
            } else if (value.includes('@') && value.length > 3) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                feedback.innerHTML = `
                    <span class="text-warning">
                        <i class="fas fa-info-circle me-1"></i>Must end with @cit.edu
                    </span>
                `;
            } else {
                this.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = '';
            }
        });
    }
    
    // Student ID Validation
    const studIdField = document.querySelector('input[name="stud_id"]');
    if (studIdField) {
        const feedback = createFeedbackElement();
        studIdField.parentElement.appendChild(feedback);
        
        studIdField.addEventListener('input', function() {
            const value = this.value.trim();
            const validFormat = /^\d{2}-\d{4}-\d{3}$/.test(value);
            
            if (validFormat) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
                feedback.innerHTML = `
                    <span class="text-success">
                        <i class="fas fa-check-circle me-1"></i>Format looks good!
                    </span>
                `;
            } else if (value.length > 0) {
                this.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = `
                    <span class="text-muted">
                        <i class="fas fa-keyboard me-1"></i>Format: ##-####-### (e.g., 21-1234-567)
                    </span>
                `;
            } else {
                this.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = '';
            }
        });
    }
    
    // Personal Email Validation (basic)
    const personalEmailField = document.querySelector('input[name="personal_email"]');
    if (personalEmailField) {
        const feedback = createFeedbackElement();
        personalEmailField.parentElement.appendChild(feedback);
        
        personalEmailField.addEventListener('input', function() {
            const value = this.value.toLowerCase().trim();
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (emailPattern.test(value)) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
                feedback.innerHTML = `
                    <span class="text-success">
                        <i class="fas fa-check-circle me-1"></i>Email format is valid
                    </span>
                `;
            } else if (value.length > 0) {
                this.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = `
                    <span class="text-muted">
                        <i class="fas fa-envelope me-1"></i>Enter a valid email address
                    </span>
                `;
            } else {
                this.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = '';
            }
        });
    }
}

// ============================================================================
// Password Strength Indicator (Compact with Real-time Checkmarks)
// ============================================================================
function initPasswordStrength() {
    const password1Field = document.querySelector('input[name="password1"]');
    if (!password1Field) return;
    
    const strengthHTML = `
        <div class="password-requirements" style="display: none;">
            <div class="requirement-item">
                <i class="fas fa-circle requirement-icon"></i>
                <span class="requirement-text">At least 8 characters</span>
            </div>
            <div class="requirement-item">
                <i class="fas fa-circle requirement-icon"></i>
                <span class="requirement-text">Upper & lowercase letters</span>
            </div>
            <div class="requirement-item">
                <i class="fas fa-circle requirement-icon"></i>
                <span class="requirement-text">At least one number</span>
            </div>
            <div class="requirement-item">
                <i class="fas fa-circle requirement-icon"></i>
                <span class="requirement-text">Special character (!@#$%^&*)</span>
            </div>
        </div>
    `;
    
    // Find the parent div and insert after password field wrapper
    const passwordWrapper = password1Field.closest('.password-wrapper') || password1Field.parentElement;
    const parentDiv = passwordWrapper.parentElement;
    
    // Create a container for requirements
    const requirementsContainer = document.createElement('div');
    requirementsContainer.innerHTML = strengthHTML;
    const requirementsDiv = requirementsContainer.firstElementChild;
    parentDiv.appendChild(requirementsDiv);
    
    const requirementItems = requirementsDiv.querySelectorAll('.requirement-item');
    
    password1Field.addEventListener('input', function() {
        const value = this.value;
        
        // Show/hide requirements based on input
        if (value.length > 0) {
            requirementsDiv.style.display = 'block';
        } else {
            requirementsDiv.style.display = 'none';
            return;
        }
        
        // Check each requirement
        const requirements = [
            value.length >= 8,                                    // At least 8 characters
            value.match(/[a-z]/) && value.match(/[A-Z]/),       // Upper & lowercase
            value.match(/[0-9]/),                                // At least one number
            value.match(/[^a-zA-Z0-9]/)                          // Special character
        ];
        
        // Update each requirement item
        requirementItems.forEach((item, index) => {
            const icon = item.querySelector('.requirement-icon');
            const text = item.querySelector('.requirement-text');
            
            if (requirements[index]) {
                icon.classList.remove('fa-circle');
                icon.classList.add('fa-check-circle');
                icon.style.color = '#28a745';
                text.style.color = '#28a745';
                text.style.textDecoration = 'line-through';
            } else {
                icon.classList.remove('fa-check-circle');
                icon.classList.add('fa-circle');
                icon.style.color = '#6c757d';
                text.style.color = '#6c757d';
                text.style.textDecoration = 'none';
            }
        });
    });
}

// ============================================================================
// Password Match Checker
// ============================================================================
function initPasswordMatch() {
    const password1Field = document.querySelector('input[name="password1"]');
    const password2Field = document.querySelector('input[name="password2"]');
    
    if (!password1Field || !password2Field) return;
    
    const matchFeedback = createFeedbackElement();
    
    // Find parent div (not wrapper) to append feedback
    const passwordWrapper = password2Field.closest('.password-wrapper') || password2Field.parentElement;
    const parentDiv = passwordWrapper.parentElement;
    parentDiv.appendChild(matchFeedback);
    
    function checkMatch() {
        const pass1 = password1Field.value;
        const pass2 = password2Field.value;
        
        // Remove validation classes that show exclamation mark
        password2Field.classList.remove('is-valid', 'is-invalid');
        
        if (pass2.length === 0) {
            matchFeedback.innerHTML = '';
        } else if (pass1 === pass2 && pass2.length > 0) {
            matchFeedback.innerHTML = `
                <span class="text-success">
                    <i class="fas fa-check-circle me-1"></i>Passwords match perfectly!
                </span>
            `;
        } else {
            matchFeedback.innerHTML = `
                <span class="text-warning">
                    <i class="fas fa-times-circle me-1"></i>Passwords don't match yet
                </span>
            `;
        }
    }
    
    password2Field.addEventListener('input', checkMatch);
    password1Field.addEventListener('input', checkMatch);
}

// ============================================================================
// Animated Student Counter (Register Page Sidebar)
// ============================================================================
function initAnimatedCounter() {
    const counterElement = document.getElementById('studentCounter');
    if (!counterElement) return;
    
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        function update() {
            start += increment;
            if (start < target) {
                element.textContent = Math.floor(start).toLocaleString() + '+';
                requestAnimationFrame(update);
            } else {
                element.textContent = target.toLocaleString() + '+';
            }
        }
        update();
    }
    
    // Trigger counter animation after slight delay
    setTimeout(() => animateCounter(counterElement, 10000), 500);
}

// ============================================================================
// PHASE 3: POLISH & DELIGHT - Premium Features
// ============================================================================

function initPhase3Features() {
    initKeyboardShortcuts();
    initSidebarAnimations();
    initRecentActivityTicker();
    initMicroInteractions();
    initAccessibilityFeatures();
}

// ============================================================================
// Keyboard Shortcuts
// ============================================================================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Escape to close toasts
        if (e.key === 'Escape') {
            document.querySelectorAll('.toast.show').forEach(toast => {
                const toastInstance = bootstrap.Toast.getInstance(toast);
                if (toastInstance) toastInstance.hide();
            });
        }
        
        // Alt + H to go home
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            const homeLink = document.querySelector('.back-to-home');
            if (homeLink) window.location.href = homeLink.href;
        }
    });
    
    // Show keyboard hint on first visit
    if (!localStorage.getItem('keyboardHintShown')) {
        setTimeout(() => {
            showKeyboardHint();
        }, 3000);
    }
}

function showKeyboardHint() {
    const hint = document.createElement('div');
    hint.className = 'keyboard-hint position-fixed bottom-0 end-0 m-3 p-3 bg-dark text-white rounded shadow-lg';
    hint.style.zIndex = '9999';
    hint.innerHTML = `
        <small class="d-block mb-2">
            <i class="fas fa-keyboard me-2"></i><strong>Pro Tip:</strong>
        </small>
        <small>Press <kbd class="kbd-key">Alt + H</kbd> to return home anytime</small>
        <button class="btn btn-sm btn-link text-white p-0 ms-2" onclick="this.parentElement.remove(); localStorage.setItem('keyboardHintShown', 'true')">
            Got it!
        </button>
    `;
    document.body.appendChild(hint);
    
    setTimeout(() => {
        hint.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => hint.remove(), 500);
    }, 6000);
}

// ============================================================================
// Sidebar Feature Animations
// ============================================================================
function initSidebarAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.auth-sidebar li').forEach((li, index) => {
        li.style.animationDelay = `${0.5 + (index * 0.1)}s`;
        observer.observe(li);
    });
}

// ============================================================================
// Recent Activity Ticker (Register Page)
// ============================================================================
function initRecentActivityTicker() {
    const tickerElement = document.getElementById('recentSignup');
    if (!tickerElement) return;
    
    const names = ['Sarah M.', 'John D.', 'Maria G.', 'Alex K.', 'Emma R.', 'David L.', 'Sofia P.', 'Ryan T.'];
    let nameIndex = 0;
    
    function updateTicker() {
        const nameElement = tickerElement.querySelector('.signup-name');
        nameElement.style.animation = 'fadeOut 0.3s ease';
        
        setTimeout(() => {
            nameIndex = (nameIndex + 1) % names.length;
            nameElement.textContent = names[nameIndex];
            nameElement.style.animation = 'fadeIn 0.3s ease';
        }, 300);
    }
    
    // Update every 5 seconds
    setInterval(updateTicker, 5000);
}

// ============================================================================
// Micro-interactions
// ============================================================================
function initMicroInteractions() {
    // Add ripple effect on successful validation
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.classList.contains('is-valid') && this.value.trim()) {
                createSuccessRipple(this);
            }
        });
    });
    
    // Animate icons on hover
    document.querySelectorAll('.feature-icon').forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.animation = 'iconBounce 0.6s ease';
        });
        
        icon.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
}

function createSuccessRipple(element) {
    const ripple = document.createElement('div');
    ripple.className = 'success-ripple';
    element.parentElement.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// ============================================================================
// Accessibility Features
// ============================================================================
function initAccessibilityFeatures() {
    // Focus trap for modals
    const firstInput = document.querySelector('.auth-body input:first-of-type');
    if (firstInput) {
        // Auto-focus first input after page loads
        setTimeout(() => firstInput.focus(), 500);
    }
    
    // Add ARIA live regions for dynamic content
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'visually-hidden';
    liveRegion.id = 'ariaLiveRegion';
    document.body.appendChild(liveRegion);
    
    // Announce form validation results
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('blur', function() {
            const feedback = this.parentElement.querySelector('.feedback-message');
            if (feedback && feedback.textContent.trim()) {
                announceToScreenReader(feedback.textContent);
            }
        });
    });
}

function announceToScreenReader(message) {
    const liveRegion = document.getElementById('ariaLiveRegion');
    if (liveRegion) {
        liveRegion.textContent = message;
        setTimeout(() => liveRegion.textContent = '', 3000);
    }
}

// ============================================================================
// Utility Functions
// ============================================================================

function createFeedbackElement() {
    const feedback = document.createElement('div');
    feedback.className = 'feedback-message mt-1 small';
    return feedback;
}

// ============================================================================
// Initialize tooltips (if Bootstrap is available)
// ============================================================================
if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
}

console.log('✨ All Auth Enhancement Phases Initialized!');
