/* Password Reset JavaScript */

// Password toggle functionality
function initPasswordToggle() {
    document.querySelectorAll('.toggle-password-btn').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = this.querySelector('.eye-icon');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.src = icon.src.replace('eye-outline', 'eye-solid');
            } else {
                input.type = 'password';
                icon.src = icon.src.replace('eye-solid', 'eye-outline');
            }
        });
    });
}

// Password strength checker
function initPasswordStrength() {
    const passwordInput = document.getElementById('id_new_password1');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    if (!passwordInput || !strengthBar || !strengthText) return;
    
    function checkPasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        return strength;
    }
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = checkPasswordStrength(password);
        
        let percentage = 0;
        let strengthClass = '';
        let strengthLabel = '';
        
        if (password.length === 0) {
            percentage = 0;
            strengthLabel = '';
        } else if (strength <= 2) {
            percentage = 25;
            strengthClass = 'strength-weak';
            strengthLabel = 'Weak';
        } else if (strength <= 4) {
            percentage = 50;
            strengthClass = 'strength-fair';
            strengthLabel = 'Fair';
        } else if (strength <= 5) {
            percentage = 75;
            strengthClass = 'strength-good';
            strengthLabel = 'Good';
        } else {
            percentage = 100;
            strengthClass = 'strength-strong';
            strengthLabel = 'Strong';
        }
        
        strengthBar.style.width = percentage + '%';
        strengthBar.className = 'password-strength-bar ' + strengthClass;
        strengthText.textContent = strengthLabel;
        strengthText.className = 'password-strength-text ' + strengthClass;
    });
}

// Form validation for password match
function initPasswordFormValidation() {
    const form = document.getElementById('setPasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const password1 = document.getElementById('id_new_password1').value;
        const password2 = document.getElementById('id_new_password2').value;
        
        if (password1 !== password2) {
            e.preventDefault();
            if (typeof showErrorToast === 'function') {
                showErrorToast('Passwords do not match');
            } else {
                alert('Passwords do not match');
            }
        }
    });
}

// Request new reset link (for invalid links)
function initRequestNewLink() {
    const requestNewLinkBtn = document.getElementById('requestNewLinkBtn');
    if (requestNewLinkBtn) {
        requestNewLinkBtn.addEventListener('click', function() {
            const resetUrl = this.getAttribute('data-reset-url');
            if (resetUrl) {
                window.location.href = resetUrl;
            }
        });
    }
}

// Countdown and auto-redirect (password_reset_complete.html)
function initCountdownRedirect(seconds, redirectUrl) {
    const countdownEl = document.getElementById('countdown');
    const goToLoginBtn = document.getElementById('goToLoginBtn');
    
    if (!countdownEl) return;
    
    let timeLeft = seconds;
    
    const countdown = setInterval(() => {
        timeLeft--;
        countdownEl.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(countdown);
            window.location.href = redirectUrl;
        }
    }, 1000);
    
    if (goToLoginBtn) {
        goToLoginBtn.addEventListener('click', function() {
            clearInterval(countdown);
            window.location.href = redirectUrl;
        });
    }
}

// Initialize all password reset functionality
document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
    initPasswordStrength();
    initPasswordFormValidation();
    initRequestNewLink();
});
