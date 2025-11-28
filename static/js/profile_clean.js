/**
 * Profile Page JavaScript - Clean Version
 * Focused on core profile management features only
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab from URL hash or localStorage
    initializeActiveTab();
    
    // Bio character count
    const bioTextarea = document.getElementById('bio');
    if (bioTextarea) {
        const charCount = document.getElementById('bioCharCount');
        bioTextarea.addEventListener('input', function() {
            if (charCount) {
                charCount.textContent = this.value.length;
            }
        });
    }
    
    // Phone number validation
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            const invalidChars = /[^0-9+\-\s]/g;
            if (invalidChars.test(this.value)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
        
        // Validate on blur
        phoneInput.addEventListener('blur', function() {
            if (this.value && !/^[0-9+\-\s]+$/.test(this.value)) {
                this.classList.add('is-invalid');
            }
        });
    }
    
    // Track form changes for unsaved changes warning
    initializeFormChangeTracking();
    
    // Show edit mode if there are form errors
    showEditModeWithErrors();
});

// ==================== PHOTO UPLOAD ====================
function handlePhotoUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        input.value = '';
        return;
    }
    
    // Validate file type
    if (!file.type.match('image.*')) {
        alert('Please select an image file');
        input.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const profileImage = document.getElementById('profileImage');
        if (profileImage) {
            profileImage.src = e.target.result;
        }
    };
    reader.readAsDataURL(file);
    
    // Submit form automatically
    const form = document.getElementById('photoUploadForm');
    if (form) {
        form.submit();
    }
}

// ==================== TAB SWITCHING ====================
function switchTab(tabName) {
    // Remove active class from all tabs and panels
    const allTabBtns = document.querySelectorAll('.profile-tab-btn');
    const allTabPanels = document.querySelectorAll('.profile-tab-panel');
    
    allTabBtns.forEach(btn => btn.classList.remove('active'));
    allTabPanels.forEach(panel => panel.classList.remove('active'));
    
    // Add active class to selected tab and panel
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    const activePanel = document.getElementById(`${tabName}-tab`);
    
    if (activeBtn && activePanel) {
        activeBtn.classList.add('active');
        activePanel.classList.add('active');
        
        // Save active tab to localStorage
        localStorage.setItem('profileActiveTab', tabName);
        
        // Update URL hash (without scrolling)
        history.replaceState(null, null, `#${tabName}`);
    }
}

function initializeActiveTab() {
    // Check URL hash first, then localStorage, then default to 'personal'
    let activeTab = window.location.hash.replace('#', '');
    
    if (!activeTab || !document.getElementById(`${activeTab}-tab`)) {
        activeTab = localStorage.getItem('profileActiveTab') || 'personal';
    }
    
    // Validate tab exists
    if (!document.getElementById(`${activeTab}-tab`)) {
        activeTab = 'personal';
    }
    
    switchTab(activeTab);
}

// ==================== EDIT MODE TOGGLE ====================
function toggleEditMode(cardId) {
    const displayDiv = document.getElementById(cardId + '-display');
    const editDiv = document.getElementById(cardId + '-edit');
    
    if (displayDiv && editDiv) {
        if (editDiv.classList.contains('active')) {
            // Switch to display mode
            editDiv.classList.remove('active');
            if (cardId === 'bioInfo') {
                displayDiv.style.display = 'block';
            } else {
                displayDiv.style.display = 'grid';
            }
            // Reset form dirty state
            window.formDirty = false;
        } else {
            // Switch to edit mode
            displayDiv.style.display = 'none';
            editDiv.classList.add('active');
            // Set form dirty state to false initially
            window.formDirty = false;
        }
    }
}

function cancelEdit(cardId) {
    // Check if form has unsaved changes
    if (window.formDirty) {
        showConfirmModal(
            'Unsaved Changes',
            'You have unsaved changes. Do you want to discard them?',
            function() {
                // User confirmed - discard changes
                const form = document.querySelector(`#${cardId}-edit form`);
                if (form) {
                    form.reset();
                }
                toggleEditMode(cardId);
                window.formDirty = false;
            }
        );
        return;
    }
    
    // No unsaved changes - just close
    const form = document.querySelector(`#${cardId}-edit form`);
    if (form) {
        form.reset();
    }
    toggleEditMode(cardId);
}

// ==================== FORM CHANGE TRACKING ====================
let formDirty = false;

function initializeFormChangeTracking() {
    // Track changes in all forms
    const forms = document.querySelectorAll('.edit-form-container form');
    
    forms.forEach(form => {
        // Track input changes
        const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                window.formDirty = true;
            });
            
            input.addEventListener('input', function() {
                window.formDirty = true;
            });
        });
        
        // Add form submission validation
        form.addEventListener('submit', function(e) {
            // Validate required fields before submission
            const requiredFields = form.querySelectorAll('[required]');
            let hasErrors = false;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    e.preventDefault();
                    field.classList.add('is-invalid');
                    showToast('error', `${field.previousElementSibling?.textContent.replace('*', '').trim() || 'Required field'} cannot be empty`);
                    hasErrors = true;
                }
            });
            
            // Validate email format
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                if (field.value && !isValidEmail(field.value)) {
                    e.preventDefault();
                    field.classList.add('is-invalid');
                    showToast('error', 'Please enter a valid email address');
                    hasErrors = true;
                }
            });
            
            if (!hasErrors) {
                window.formDirty = false;
            }
        });
    });
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Toast notification function
function showToast(type, message) {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-messages-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-messages-container';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Determine icon
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    else if (type === 'error' || type === 'danger') icon = 'times-circle';
    else if (type === 'warning') icon = 'exclamation-triangle';
    
    toast.innerHTML = `
        <div class="toast-notification__content">
            <i class="toast-notification__icon fas fa-${icon}"></i>
            <span class="toast-notification__message">${message}</span>
        </div>
        <button type="button" class="toast-notification__close" aria-label="Close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ==================== UNSAVED CHANGES WARNING ====================
window.addEventListener('beforeunload', function(e) {
    // Check if any edit form is active
    const activeEditForm = document.querySelector('.edit-form-container.active');
    
    if (activeEditForm && window.formDirty) {
        // Modern browsers will show their own message
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Warn when navigating away from edit mode with unsaved changes
document.addEventListener('click', function(e) {
    // Check if clicking a navigation link
    const link = e.target.closest('a[href]');
    if (link && !link.href.startsWith('javascript:') && !link.getAttribute('href').startsWith('#')) {
        const activeEditForm = document.querySelector('.edit-form-container.active');
        
        if (activeEditForm && window.formDirty) {
            e.preventDefault();
            showConfirmModal(
                'Unsaved Changes',
                'You have unsaved changes. Do you want to leave this page?',
                function() {
                    // User confirmed - navigate away
                    window.formDirty = false;
                    window.location.href = link.href;
                }
            );
            return false;
        }
    }
});

// ==================== CUSTOM CONFIRM MODAL ====================
function showConfirmModal(title, message, onConfirm) {
    // Remove existing modal if any
    const existingModal = document.getElementById('customConfirmModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'customConfirmModal';
    modal.className = 'custom-confirm-modal';
    modal.innerHTML = `
        <div class="custom-confirm-overlay"></div>
        <div class="custom-confirm-content">
            <div class="custom-confirm-header">
                <h3 class="custom-confirm-title">
                    <i class="fas fa-exclamation-triangle text-warning"></i>
                    ${title}
                </h3>
            </div>
            <div class="custom-confirm-body">
                <p>${message}</p>
            </div>
            <div class="custom-confirm-footer">
                <button type="button" class="btn btn-secondary" id="confirmModalCancel">
                    Continue Editing
                </button>
                <button type="button" class="btn btn-danger" id="confirmModalConfirm">
                    Discard Changes
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    document.getElementById('confirmModalCancel').addEventListener('click', function() {
        modal.remove();
    });
    
    document.getElementById('confirmModalConfirm').addEventListener('click', function() {
        modal.remove();
        if (onConfirm) onConfirm();
    });
    
    // Close on overlay click
    modal.querySelector('.custom-confirm-overlay').addEventListener('click', function() {
        modal.remove();
    });
    
    // Show modal with animation
    setTimeout(() => modal.classList.add('show'), 10);
}

// ==================== FORM ERROR HANDLING ====================
function showEditModeWithErrors() {
    // Check if any form has validation errors
    const formsWithErrors = [
        { id: 'personalInfo', form: document.getElementById('personalInfoForm') },
        { id: 'academicInfo', form: document.getElementById('academicInfoForm') },
        { id: 'bioInfo', form: document.getElementById('bioInfoForm') }
    ];
    
    formsWithErrors.forEach(({ id, form }) => {
        if (form && form.querySelector('.is-invalid')) {
            // Show edit mode for this form
            const displayDiv = document.getElementById(id + '-display');
            const editDiv = document.getElementById(id + '-edit');
            
            if (displayDiv && editDiv) {
                displayDiv.style.display = 'none';
                editDiv.classList.add('active');
                
                // Switch to appropriate tab
                if (id === 'personalInfo') {
                    switchTab('personal');
                } else if (id === 'academicInfo') {
                    switchTab('academic');
                } else if (id === 'bioInfo') {
                    switchTab('about');
                }
            }
        }
    });
}
