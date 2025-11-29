/**
 * Toast Notification System
 * Unified toast system for both Django messages and JavaScript notifications
 */

(function() {
    'use strict';

    /**
     * Initialize Django messages as toasts
     * Auto-dismiss after 5 seconds
     */
    function initDjangoToasts() {
        const toasts = document.querySelectorAll('.toast-notification[data-autohide="true"]');
        
        toasts.forEach(toast => {
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                dismissToast(toast);
            }, 5000);
        });
    }

    /**
     * Dismiss a toast with animation
     * @param {HTMLElement} toast - The toast element to dismiss
     */
    function dismissToast(toast) {
        if (!toast) return;
        
        toast.classList.add('toast-hiding');
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
                
                // Remove container if no more toasts
                const container = document.querySelector('.toast-messages-container');
                if (container && container.children.length === 0) {
                    container.remove();
                }
            }
        }, 300);
    }

    /**
     * Show a toast notification (for JavaScript-triggered toasts)
     * @param {string} message - The message to display
     * @param {string} type - Type of toast (success, error, warning, info)
     * @param {number} duration - Auto-dismiss duration in ms (default: 5000)
     * @returns {HTMLElement} The created toast element
     */
    window.showToast = function(message, type = 'success', duration = 5000) {
        // Get or create container
        let container = document.querySelector('.toast-messages-container');
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-messages-container';
            document.body.appendChild(container);
        }

        // Map type aliases
        const typeMap = {
            'error': 'error',
            'danger': 'error',
            'success': 'success',
            'warning': 'warning',
            'info': 'info'
        };
        
        const toastType = typeMap[type] || 'info';

        // Map icons
        const iconMap = {
            'success': 'fa-check-circle',
            'error': 'fa-times-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${toastType}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="toast-notification__content">
                <i class="toast-notification__icon fas ${iconMap[toastType]}"></i>
                <span class="toast-notification__message">${escapeHtml(message)}</span>
            </div>
            <button type="button" class="toast-notification__close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add close button functionality
        const closeBtn = toast.querySelector('.toast-notification__close');
        closeBtn.addEventListener('click', () => dismissToast(toast));

        // Add to container
        container.appendChild(toast);

        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                dismissToast(toast);
            }, duration);
        }

        return toast;
    };

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show success toast (convenience method)
     */
    window.showSuccessToast = function(message, duration) {
        return window.showToast(message, 'success', duration);
    };

    /**
     * Show error toast (convenience method)
     */
    window.showErrorToast = function(message, duration) {
        return window.showToast(message, 'error', duration);
    };

    /**
     * Show warning toast (convenience method)
     */
    window.showWarningToast = function(message, duration) {
        return window.showToast(message, 'warning', duration);
    };

    /**
     * Show info toast (convenience method)
     */
    window.showInfoToast = function(message, duration) {
        return window.showToast(message, 'info', duration);
    };

    /**
     * Dismiss all toasts
     */
    window.dismissAllToasts = function() {
        const toasts = document.querySelectorAll('.toast-notification');
        toasts.forEach(toast => dismissToast(toast));
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDjangoToasts);
    } else {
        initDjangoToasts();
    }

})();
