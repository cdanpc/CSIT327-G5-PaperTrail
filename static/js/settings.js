/**
 * ============================================
 * SETTINGS PAGE JAVASCRIPT
 * Version: 1.0
 * Description: Handle settings page interactions
 * ============================================
 */

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page initialized');
    initializeSettingsHandlers();
});

// ===== MAIN INITIALIZATION FUNCTION =====
function initializeSettingsHandlers() {
    // Initialize notification toggles
    initializeNotificationToggles();
    
    // Initialize select dropdowns
    initializeSelectHandlers();
    
    // Initialize button click handlers
    initializeButtonHandlers();
    
    // Initialize modal form handlers
    initializeModalForms();
}

// ===== NOTIFICATION TOGGLES =====
function initializeNotificationToggles() {
    const notificationToggles = document.querySelectorAll('.notification-toggle');
    
    notificationToggles.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const settingId = this.id;
            const settingValue = this.checked;
            
            console.log(`Notification toggle changed: ${settingId} = ${settingValue}`);
            
            // Save preference via AJAX
            saveNotificationPreference(settingId, settingValue, checkbox);
        });
    });
}

// ===== SELECT DROPDOWNS =====
function initializeSelectHandlers() {
    const selects = document.querySelectorAll('.settings-select:not([disabled])');
    
    selects.forEach(select => {
        select.addEventListener('change', function() {
            const settingId = this.id || this.name;
            const settingValue = this.value;
            
            console.log(`Select changed: ${settingId} = ${settingValue}`);
            
            // Save preference (will be implemented with backend)
            saveSelectPreference(settingId, settingValue);
        });
    });
    
    // Handle preferences form submission
    const preferencesForm = document.getElementById('preferencesForm');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            savePreferencesForm(this);
        });
    }
}

// ===== BUTTON HANDLERS =====
function initializeButtonHandlers() {
    // Change Password button
    const passwordBtn = document.querySelector('[href*="password_change"]');
    if (passwordBtn) {
        passwordBtn.addEventListener('click', function(e) {
            console.log('Navigating to change password');
        });
    }
    
    // View Sessions button
    const viewSessionsBtn = document.getElementById('viewSessionsBtn');
    if (viewSessionsBtn) {
        viewSessionsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showSessionsModal();
        });
    }
    
    // Logout All Sessions button
    const logoutAllBtn = document.getElementById('logoutAllBtn');
    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showLogoutAllModal();
        });
    }
    
    // Export Data button
    const exportDataBtn = document.getElementById('exportDataBtn');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleExportData();
        });
    }
    
    // Delete Account button
    const deleteBtn = document.getElementById('deleteAccountBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showDeleteAccountModal();
        });
    }
}

// ===== SAVE FUNCTIONS =====
/**
 * Save notification preference via AJAX (Enhanced - Phase 7)
 * @param {string} settingId - The ID of the setting
 * @param {boolean} value - The new value
 * @param {HTMLElement} checkbox - The checkbox element
 */
function saveNotificationPreference(settingId, value, checkbox) {
    // Add visual feedback - disable during save
    checkbox.disabled = true;
    
    const formData = new FormData();
    formData.append('update_notification', '1');
    formData.append('notification_type', settingId);
    formData.append('value', value);
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    // Use retry mechanism for better reliability
    const makeRequest = () => fetch(window.location.href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    }).then(response => response.json());
    
    retryRequest(makeRequest, 2, 500)
    .then(response => response)
    .then(data => {
        if (data.success) {
            showToast('Notification preference updated', 'success');
        } else {
            showToast('Failed to update preference', 'error');
            // Revert checkbox state on error
            checkbox.checked = !value;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Connection error. Please check your internet.', 'error');
        // Revert checkbox state on error
        checkbox.checked = !value;
    })
    .finally(() => {
        // Re-enable checkbox
        checkbox.disabled = false;
    });
}

/**
 * Save select preference
 * @param {string} settingId - The ID of the setting
 * @param {string} value - The new value
 */
function saveSelectPreference(settingId, value) {
    // Handle profile visibility separately with AJAX
    if (settingId === 'profileVisibility') {
        savePrivacyPreference('profileVisibility', value);
        return;
    }
    
    // Handle default dashboard (Auto-save)
    if (settingId === 'default_dashboard' || settingId === 'defaultDashboard') {
        const formData = new FormData();
        formData.append('save_preferences', '1');
        formData.append('default_dashboard', value);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Preferences saved successfully!', 'success');
            } else {
                showToast(data.message || 'Failed to save preferences', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Connection error. Please check your internet.', 'error');
        });
        return;
    }
    
    // For other preferences, we'll let the form handle it
    // Individual selects will just show visual feedback
    console.log(`Preference marked for save: ${settingId} = ${value}`);
}

/**
 * Save privacy preference via AJAX
 * @param {string} privacyType - The type of privacy setting
 * @param {string} value - The new value
 */
function savePrivacyPreference(privacyType, value) {
    const formData = new FormData();
    formData.append('update_privacy', '1');
    formData.append('privacy_type', privacyType);
    formData.append('value', value);
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Privacy settings updated', 'success');
        } else {
            showToast('Failed to update privacy settings', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    });
}

/**
 * Save preferences form via AJAX (Enhanced - Phase 7)
 * @param {HTMLFormElement} form - The form element
 */
function savePreferencesForm(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
    
    fetch(form.action || window.location.href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Preferences saved successfully!', 'success');
            
            // Update UI to reflect changes without reload
            const dashboard = formData.get('default_dashboard');
            const language = formData.get('language');
            
            // Update any displayed preference values
            updatePreferenceDisplay(dashboard, language);
            
            // Optional: Only reload if language changed (for translations)
            if (language && data.language_changed) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            showToast(data.message || 'Failed to save preferences', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to save preferences', 'error');
    })
    .finally(() => {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    });
}

/**
 * Update preference display after save
 * @param {string} dashboard - Dashboard preference
 * @param {string} language - Language preference
 */
function updatePreferenceDisplay(dashboard, language) {
    // Update any UI elements that show current preferences
    console.log('Preferences updated:', { dashboard, language });
}

// ===== TOAST NOTIFICATION SYSTEM =====
/**
 * Show toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast (success, error, warning)
 */
function showToast(message, type = 'success') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    // Set icon based on type
    let icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-times-circle';
    if (type === 'warning') icon = 'fa-exclamation-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span class="toast-message">${message}</span>
    `;
    
    // Add to DOM
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// ===== MODAL FUNCTIONS =====
/**
 * Show delete account confirmation modal
 */
function showDeleteAccountModal() {
    // Create modal HTML
    const modalHTML = `
        <div class="modal fade" id="deleteAccountModal" tabindex="-1" aria-labelledby="deleteAccountModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="deleteAccountModalLabel">
                            <i class="fas fa-exclamation-triangle text-danger"></i>
                            Delete Account
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">Are you absolutely sure you want to delete your account?</p>
                        <div class="alert alert-danger mb-3">
                            <i class="fas fa-exclamation-circle"></i>
                            <strong>Warning:</strong> This action cannot be undone!
                        </div>
                        <ul class="text-danger mb-3">
                            <li>All your uploaded resources will be deleted</li>
                            <li>Your profile and activity history will be permanently removed</li>
                            <li>You will lose access to all bookmarks and saved content</li>
                            <li>This action is irreversible</li>
                        </ul>
                        <p class="mb-0">If you're sure, please type <strong>DELETE</strong> below to confirm:</p>
                        <input type="text" class="form-control mt-2" id="deleteConfirmInput" placeholder="Type DELETE to confirm">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn" disabled>Delete My Account</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('deleteAccountModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Initialize modal
    const modalElement = document.getElementById('deleteAccountModal');
    const modal = new bootstrap.Modal(modalElement);
    
    // Handle confirmation input
    const confirmInput = document.getElementById('deleteConfirmInput');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    confirmInput.addEventListener('input', function() {
        if (this.value === 'DELETE') {
            confirmBtn.disabled = false;
        } else {
            confirmBtn.disabled = true;
        }
    });
    
    // Handle delete confirmation
    confirmBtn.addEventListener('click', function() {
        handleDeleteAccount();
        modal.hide();
    });
    
    // Clean up modal after hiding
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalElement.remove();
    });
    
    // Show modal
    modal.show();
}

/**
 * Handle account deletion
 */
function handleDeleteAccount() {
    const confirmInput = document.getElementById('deleteConfirmInput');
    const confirmText = confirmInput ? confirmInput.value : '';
    
    if (confirmText !== 'DELETE') {
        showToast('Please type DELETE to confirm', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('confirm_text', confirmText);
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch('/accounts/delete-account/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Account deletion scheduled. You have 7 days to cancel. Logging out...', 'success');
            setTimeout(() => {
                window.location.href = data.redirect || '/';
            }, 2000);
        } else {
            showToast(data.message || 'Failed to delete account', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while deleting account', 'error');
    });
}

/**
 * Show sessions modal (view active devices)
 */
function showSessionsModal() {
    // Fetch sessions from backend
    fetch('/accounts/sessions/view/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.sessions) {
            displaySessionsModal(data.sessions);
        } else {
            showToast('Failed to load sessions', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while loading sessions', 'error');
    });
}

/**
 * Display sessions in a modal
 * @param {Array} sessions - Array of session objects
 */
function displaySessionsModal(sessions) {
    let sessionsHTML = '';
    
    if (sessions.length === 0) {
        sessionsHTML = '<p class="text-muted text-center py-3">No active sessions found.</p>';
    } else {
        sessions.forEach(session => {
            const currentBadge = session.is_current ? '<span class="badge bg-success ms-2">Current Session</span>' : '';
            const activeBadge = session.is_active ? '<span class="badge bg-primary ms-2">Active</span>' : '<span class="badge bg-secondary ms-2">Inactive</span>';
            
            sessionsHTML += `
                <div class="session-item mb-3 p-3 border rounded">
                    <div class="d-flex align-items-start">
                        <div class="session-icon me-3">
                            <i class="fas ${session.device_icon} fa-2x text-primary"></i>
                        </div>
                        <div class="session-info flex-grow-1">
                            <h6 class="mb-1">
                                ${session.device_name}
                                ${currentBadge}
                                ${activeBadge}
                            </h6>
                            <p class="mb-1 text-muted small">
                                <i class="fas fa-globe me-1"></i> ${session.browser}
                            </p>
                            <p class="mb-1 text-muted small">
                                <i class="fas fa-network-wired me-1"></i> ${session.ip_address} ${session.location !== 'Unknown Location' ? '(' + session.location + ')' : ''}
                            </p>
                            <p class="mb-0 text-muted small">
                                <i class="fas fa-clock me-1"></i> Last active ${session.last_activity} ago
                            </p>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    const modalHTML = `
        <div class="modal fade" id="sessionsModal" tabindex="-1" aria-labelledby="sessionsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="sessionsModalLabel">
                            <i class="fas fa-laptop me-2"></i>
                            Active Sessions
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted mb-3">
                            These are the devices where you're currently logged in. If you see a session you don't recognize, logout from all devices immediately.
                        </p>
                        ${sessionsHTML}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('sessionsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Get modal element
    const modalElement = document.getElementById('sessionsModal');
    const modal = new bootstrap.Modal(modalElement);
    
    // Cleanup on close
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalElement.remove();
    });
    
    // Show modal
    modal.show();
}

/**
 * Show logout all sessions confirmation modal
 */
function showLogoutAllModal() {
    const modalHTML = `
        <div class="modal fade" id="logoutAllModal" tabindex="-1" aria-labelledby="logoutAllModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="logoutAllModalLabel">
                            <i class="fas fa-sign-out-alt text-warning"></i>
                            Logout All Sessions
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">This will sign you out from all devices except this one.</p>
                        <div class="alert alert-warning">
                            <i class="fas fa-info-circle"></i>
                            You'll need to sign in again on those devices.
                        </div>
                        <p class="mb-0">Are you sure you want to continue?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-warning" id="confirmLogoutAllBtn">Logout All Devices</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('logoutAllModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Get modal element
    const modalElement = document.getElementById('logoutAllModal');
    const modal = new bootstrap.Modal(modalElement);
    
    // Handle confirm button
    const confirmBtn = document.getElementById('confirmLogoutAllBtn');
    confirmBtn.addEventListener('click', function() {
        handleLogoutAllSessions();
        modal.hide();
    });
    
    // Cleanup on close
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalElement.remove();
    });
    
    // Show modal
    modal.show();
}

/**
 * Handle logout all sessions
 */
function handleLogoutAllSessions() {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch('/accounts/sessions/logout-all/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // Close any open modals
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        } else {
            showToast('Failed to logout from other devices', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    });
}

/**
 * Handle data export
 */
function handleExportData() {
    // Show loading toast
    showToast('Preparing your data export...', 'success');
    
    // Redirect to download endpoint
    // Using window.location to trigger file download
    window.location.href = '/accounts/export-data/';
    
    // Show completion message after a delay
    setTimeout(() => {
        showToast('Your data has been downloaded!', 'success');
    }, 1000);
}

/**
 * Handle data download (legacy function - keeping for compatibility)
 */
function handleDownloadData() {
    handleExportData();
    
    // Simulate API call
    /*
    fetch('/api/account/download-data', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'papertrail-data.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        showToast('Data downloaded successfully', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to download data', 'error');
    });
    */
}

// ===== UTILITY FUNCTIONS =====
/**
 * Get CSRF token from cookie
 * @returns {string} CSRF token
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== FORM VALIDATION =====
/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Valid or not
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} Validation result with strength and message
 */
function validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    let strength = 0;
    let messages = [];
    
    if (password.length >= minLength) strength++;
    else messages.push('At least 8 characters');
    
    if (hasUpperCase) strength++;
    else messages.push('One uppercase letter');
    
    if (hasLowerCase) strength++;
    else messages.push('One lowercase letter');
    
    if (hasNumbers) strength++;
    else messages.push('One number');
    
    if (hasSpecialChar) strength++;
    else messages.push('One special character');
    
    return {
        strength: strength,
        valid: strength >= 4,
        messages: messages
    };
}

// ===== LOADING UTILITIES (Phase 7) =====
/**
 * Show loading spinner on button
 * @param {HTMLElement} button - Button element
 * @param {string} text - Loading text
 * @returns {string} Original button HTML
 */
function showButtonLoading(button, text = 'Loading...') {
    const originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
    return originalHtml;
}

/**
 * Restore button to original state
 * @param {HTMLElement} button - Button element
 * @param {string} originalHtml - Original button HTML
 */
function hideButtonLoading(button, originalHtml) {
    button.disabled = false;
    button.innerHTML = originalHtml;
}

/**
 * Debounce function for input events
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show confirmation dialog with custom message
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {Function} onConfirm - Callback on confirm
 * @param {string} confirmText - Confirm button text
 * @param {string} confirmClass - Confirm button class
 */
function showConfirmDialog(title, message, onConfirm, confirmText = 'Confirm', confirmClass = 'btn-primary') {
    const modalHTML = `
        <div class="modal fade" id="confirmDialog" tabindex="-1" aria-labelledby="confirmDialogLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="confirmDialogLabel">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn ${confirmClass}" id="confirmDialogBtn">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing dialog
    const existingDialog = document.getElementById('confirmDialog');
    if (existingDialog) {
        existingDialog.remove();
    }
    
    // Add to DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modalElement = document.getElementById('confirmDialog');
    const modal = new bootstrap.Modal(modalElement);
    
    // Handle confirm
    document.getElementById('confirmDialogBtn').addEventListener('click', function() {
        modal.hide();
        if (onConfirm) onConfirm();
    });
    
    // Cleanup
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalElement.remove();
    });
    
    modal.show();
}

/**
 * Retry failed request with exponential backoff
 * @param {Function} requestFunc - Function that returns a Promise
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} delay - Initial delay in ms
 * @returns {Promise} Request result
 */
async function retryRequest(requestFunc, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await requestFunc();
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            
            // Show retry message
            showToast(`Connection failed. Retrying... (${i + 1}/${maxRetries})`, 'warning');
            
            // Wait with exponential backoff
            await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        }
    }
}

// ===== KEYBOARD SHORTCUTS (Phase 7) =====
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save preferences
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const preferencesForm = document.getElementById('preferencesForm');
        if (preferencesForm) {
            preferencesForm.dispatchEvent(new Event('submit'));
            showToast('Saving preferences...', 'info');
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// ===== MODAL FORM HANDLERS =====
function initializeModalForms() {
    // Password Change Modal
    const passwordChangeForm = document.getElementById('passwordChangeForm');
    const newPassword1 = document.getElementById('new_password1');
    
    if (newPassword1) {
        const passwordRequirements = document.getElementById('passwordRequirements');
        
        newPassword1.addEventListener('input', function() {
            if (passwordRequirements) {
                passwordRequirements.style.display = 'block';
                validatePasswordRequirements(this.value);
            }
        });
    }
    
    if (passwordChangeForm) {
        passwordChangeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const oldPassword = document.getElementById('old_password').value;
            const newPassword1 = document.getElementById('new_password1').value;
            const newPassword2 = document.getElementById('new_password2').value;
            
            // Validate passwords match
            if (newPassword1 !== newPassword2) {
                showToast('error', 'Passwords do not match');
                return;
            }
            
            // Validate password requirements
            if (!validatePasswordFormat(newPassword1)) {
                showToast('error', 'Password does not meet requirements');
                return;
            }
            
            // Submit form
            this.submit();
        });
    }
    
    // University Email Change Modal
    const changeUnivEmailForm = document.getElementById('changeUnivEmailForm');
    if (changeUnivEmailForm) {
        changeUnivEmailForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const newEmail = document.getElementById('new_univ_email').value;
            const reason = document.getElementById('reason').value;
            const password = document.getElementById('password_univ').value;
            
            // Basic validation
            if (!newEmail || !reason || !password) {
                showToast('error', 'Please fill in all fields');
                return;
            }
            
            if (!validateEmail(newEmail)) {
                showToast('error', 'Please enter a valid email address');
                return;
            }
            
            // Submit form
            this.submit();
        });
    }
}

function validatePasswordRequirements(password) {
    const requirements = {
        length: password.length >= 8,
        letter: /[a-zA-Z]/.test(password),
        number: /\d/.test(password)
    };
    
    // Update requirement indicators
    updateRequirementIndicator('req-length', requirements.length);
    updateRequirementIndicator('req-letter', requirements.letter);
    updateRequirementIndicator('req-number', requirements.number);
    
    return Object.values(requirements).every(req => req);
}

function updateRequirementIndicator(elementId, met) {
    const element = document.getElementById(elementId);
    if (element) {
        const icon = element.querySelector('i');
        if (met) {
            icon.className = 'fas fa-check-circle text-success';
        } else {
            icon.className = 'fas fa-circle text-muted';
        }
    }
}

function validatePasswordFormat(password) {
    return password.length >= 8 && 
           /[a-zA-Z]/.test(password) && 
           /\d/.test(password);
}

// Export functions for use in other scripts if needed
window.SettingsModule = {
    showToast,
    validateEmail,
    validatePassword,
    getCSRFToken,
    showButtonLoading,
    hideButtonLoading,
    debounce,
    showConfirmDialog,
    retryRequest
};

console.log('Settings module loaded successfully (Phase 7 Enhanced)');
