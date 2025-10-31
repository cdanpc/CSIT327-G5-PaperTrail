/**
 * Password Change Page JavaScript
 * Version: 2.0 - Enhanced with visual password strength indicator
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passwordChangeForm');
    const newPassword1 = document.querySelector('input[name="new_password1"]');
    const newPassword2 = document.querySelector('input[name="new_password2"]');
    
    // Password strength indicator elements
    const strengthContainer = document.getElementById('passwordStrengthContainer');
    const strengthFill = document.getElementById('passwordStrengthFill');
    const strengthText = document.getElementById('passwordStrengthText');
    const reqLength = document.getElementById('req-length');
    const reqLetter = document.getElementById('req-letter');
    const reqNumber = document.getElementById('req-number');
    
    // Real-time password strength indicator
    if (newPassword1 && strengthContainer) {
        newPassword1.addEventListener('input', function() {
            const password = this.value;
            
            // Show/hide strength indicator
            if (password.length > 0) {
                strengthContainer.style.display = 'block';
            } else {
                strengthContainer.style.display = 'none';
                return;
            }
            
            // Check requirements
            const requirements = {
                length: password.length >= 8,
                hasLetter: /[A-Za-z]/.test(password),
                hasNumber: /\d/.test(password)
            };
            
            // Update requirement indicators
            updateRequirement(reqLength, requirements.length);
            updateRequirement(reqLetter, requirements.hasLetter);
            updateRequirement(reqNumber, requirements.hasNumber);
            
            // Calculate strength
            const metRequirements = Object.values(requirements).filter(Boolean).length;
            let strengthLevel = 'weak';
            let strengthLabel = 'Weak';
            
            if (metRequirements === 3) {
                strengthLevel = 'strong';
                strengthLabel = 'Strong';
            } else if (metRequirements === 2) {
                strengthLevel = 'medium';
                strengthLabel = 'Medium';
            }
            
            // Update strength bar
            strengthFill.className = 'password-strength-fill ' + strengthLevel;
            strengthText.className = 'password-strength-text ' + strengthLevel;
            strengthText.textContent = strengthLabel;
            
            // Visual feedback on input
            if (metRequirements === 3) {
                newPassword1.classList.remove('is-invalid');
                newPassword1.classList.add('is-valid');
            } else {
                newPassword1.classList.remove('is-valid');
            }
        });
        
        // Hide strength indicator on blur if empty
        newPassword1.addEventListener('blur', function() {
            if (this.value.length === 0) {
                strengthContainer.style.display = 'none';
            }
        });
    }
    
    // Confirm password match validation
    if (newPassword2 && newPassword1) {
        newPassword2.addEventListener('input', function() {
            validatePasswordMatch();
        });
        
        newPassword1.addEventListener('input', function() {
            if (newPassword2.value.length > 0) {
                validatePasswordMatch();
            }
        });
    }
    
    /**
     * Update requirement indicator
     */
    function updateRequirement(element, met) {
        if (met) {
            element.classList.add('met');
            element.querySelector('i').className = 'fas fa-check-circle';
        } else {
            element.classList.remove('met');
            element.querySelector('i').className = 'fas fa-circle';
        }
    }
    
    /**
     * Validate password match
     */
    function validatePasswordMatch() {
        if (newPassword1.value && newPassword2.value) {
            if (newPassword1.value !== newPassword2.value) {
                newPassword2.classList.add('is-invalid');
                newPassword2.classList.remove('is-valid');
                newPassword2.setCustomValidity('Passwords do not match');
            } else {
                newPassword2.classList.remove('is-invalid');
                newPassword2.classList.add('is-valid');
                newPassword2.setCustomValidity('');
            }
        }
    }
    
    // Form submission validation
    if (form) {
        form.addEventListener('submit', function(e) {
            // Additional validation before submission
            const password1 = newPassword1.value;
            const password2 = newPassword2.value;
            
            // Check if passwords match
            if (password1 !== password2) {
                e.preventDefault();
                alert('Passwords do not match. Please check and try again.');
                newPassword2.focus();
                return false;
            }
            
            // Check if password meets requirements
            const meetsRequirements = 
                password1.length >= 8 &&
                /[A-Za-z]/.test(password1) &&
                /\d/.test(password1);
            
            if (!meetsRequirements) {
                e.preventDefault();
                alert('Password does not meet requirements. Please check the requirements and try again.');
                newPassword1.focus();
                return false;
            }
        });
    }
});
