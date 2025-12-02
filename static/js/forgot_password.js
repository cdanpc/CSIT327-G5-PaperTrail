/* Forgot Password Flow JavaScript */

// Step 1: Method Selection
function selectMethod(method) {
    const methodCards = document.querySelectorAll('.method-card');
    const emailSection = document.getElementById('emailSection');
    const phoneSection = document.getElementById('phoneSection');
    
    if (!methodCards.length) return;
    
    methodCards.forEach(card => card.classList.remove('active'));
    
    if (method === 'email') {
        document.getElementById('emailRadio').checked = true;
        document.querySelector('[data-method="email"]').classList.add('active');
        if (emailSection) emailSection.style.display = 'block';
        if (phoneSection) phoneSection.style.display = 'none';
    } else if (method === 'phone') {
        document.getElementById('phoneRadio').checked = true;
        document.querySelector('[data-method="phone"]').classList.add('active');
        if (phoneSection) phoneSection.style.display = 'block';
        if (emailSection) emailSection.style.display = 'none';
    }
}

// Step 2: Verification Code Input
function initCodeInputs() {
    const codeInputs = document.querySelectorAll('.code-input');
    if (!codeInputs.length) return;
    
    codeInputs.forEach((input, index) => {
        input.addEventListener('input', function(e) {
            const value = e.target.value;
            
            // Only allow numbers
            if (!/^\d*$/.test(value)) {
                e.target.value = value.replace(/\D/g, '');
                return;
            }
            
            // Move to next input if digit entered
            if (value.length === 1 && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
            
            // Update hidden input with complete code
            updateVerificationCode();
        });
        
        input.addEventListener('keydown', function(e) {
            // Move to previous input on backspace if empty
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                codeInputs[index - 1].focus();
            }
            
            // Allow arrow key navigation
            if (e.key === 'ArrowLeft' && index > 0) {
                codeInputs[index - 1].focus();
            }
            if (e.key === 'ArrowRight' && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
        });
        
        // Handle paste
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
            
            pastedData.split('').forEach((char, i) => {
                if (index + i < codeInputs.length) {
                    codeInputs[index + i].value = char;
                }
            });
            
            updateVerificationCode();
            
            // Focus last filled input
            const lastIndex = Math.min(index + pastedData.length - 1, codeInputs.length - 1);
            codeInputs[lastIndex].focus();
        });
    });
}

function updateVerificationCode() {
    const codeInputs = document.querySelectorAll('.code-input');
    const verificationCodeInput = document.getElementById('verificationCode');
    
    if (!verificationCodeInput) return;
    
    const code = Array.from(codeInputs).map(input => input.value).join('');
    verificationCodeInput.value = code;
}

// Resend Code Timer
function initResendTimer(seconds = 60) {
    const resendBtn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');
    
    if (!resendBtn || !timerSpan) return;
    
    let timeLeft = seconds;
    resendBtn.disabled = true;
    
    const countdown = setInterval(() => {
        timeLeft--;
        timerSpan.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(countdown);
            resendBtn.disabled = false;
            resendBtn.textContent = 'Resend Code';
        }
    }, 1000);
    
    resendBtn.addEventListener('click', function() {
        if (!this.disabled) {
            // Reset timer
            timeLeft = seconds;
            this.disabled = true;
            timerSpan.textContent = timeLeft;
            
            const newCountdown = setInterval(() => {
                timeLeft--;
                timerSpan.textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    clearInterval(newCountdown);
                    resendBtn.disabled = false;
                    resendBtn.textContent = 'Resend Code';
                }
            }, 1000);
            
            // Handle resend logic (AJAX call would go here)
            console.log('Resending code...');
        }
    });
}

// Step 3: Password Validation
function initPasswordValidation() {
    const password1 = document.getElementById('id_new_password1');
    const password2 = document.getElementById('id_new_password2');
    const requirementsList = document.querySelectorAll('.password-requirements li');
    
    if (!password1) return;
    
    password1.addEventListener('input', function() {
        const password = this.value;
        
        // Check each requirement
        checkRequirement(requirementsList[0], password.length >= 8);
        checkRequirement(requirementsList[1], /[a-z]/.test(password));
        checkRequirement(requirementsList[2], /[A-Z]/.test(password));
        checkRequirement(requirementsList[3], /\d/.test(password));
        checkRequirement(requirementsList[4], /[!@#$%^&*(),.?":{}|<>]/.test(password));
    });
    
    // Match validation
    if (password2) {
        password2.addEventListener('input', function() {
            if (this.value && password1.value !== this.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

function checkRequirement(element, isValid) {
    if (!element) return;
    
    if (isValid) {
        element.classList.add('valid');
        element.classList.remove('invalid');
    } else {
        element.classList.remove('valid');
        element.classList.add('invalid');
    }
}

// Password Toggle
function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = this.querySelector('i');
            
            if (!input) return;
            
            if (input.type === 'password') {
                input.type = 'text';
                if (icon) icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                if (icon) icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });
}

// Form submission with loading state
function initFormSubmission() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });
}

// Initialize all forgot password functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize based on which step we're on
    if (document.querySelector('.method-card')) {
        selectMethod('email'); // Default to email
    }
    
    if (document.querySelector('.code-input')) {
        initCodeInputs();
        initResendTimer();
    }
    
    if (document.getElementById('id_new_password1')) {
        initPasswordValidation();
        initPasswordToggles();
    }
    
    initFormSubmission();
});
