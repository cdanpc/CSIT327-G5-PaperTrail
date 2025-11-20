// Coming Soon Notification v1.0
// Shows toast notification for features in progress

class ComingSoonNotification {
    constructor() {
        this.toast = null;
        this.hideTimeout = null;
        this.init();
    }

    init() {
        // Create toast element if it doesn't exist
        if (!document.getElementById('comingSoonToast')) {
            this.createToast();
        } else {
            this.toast = document.getElementById('comingSoonToast');
        }

        // Attach click handlers to all coming-soon features
        this.attachHandlers();
    }

    createToast() {
        this.toast = document.createElement('div');
        this.toast.id = 'comingSoonToast';
        this.toast.className = 'coming-soon-toast';
        this.toast.innerHTML = `
            <div class="coming-soon-toast-icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="coming-soon-toast-content">
                <div class="coming-soon-toast-title">Coming Soon!</div>
                <p class="coming-soon-toast-message">This feature is currently under development.</p>
            </div>
            <button class="coming-soon-toast-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        `;
        document.body.appendChild(this.toast);

        // Close button handler
        const closeBtn = this.toast.querySelector('.coming-soon-toast-close');
        closeBtn.addEventListener('click', () => this.hide());
    }

    show(message = 'This feature is currently under development.', title = 'Coming Soon!') {
        if (!this.toast) return;

        // Update content
        const titleEl = this.toast.querySelector('.coming-soon-toast-title');
        const messageEl = this.toast.querySelector('.coming-soon-toast-message');
        
        if (titleEl) titleEl.textContent = title;
        if (messageEl) messageEl.textContent = message;

        // Show toast
        this.toast.classList.remove('hide');
        this.toast.classList.add('show');

        // Auto-hide after 3 seconds
        clearTimeout(this.hideTimeout);
        this.hideTimeout = setTimeout(() => this.hide(), 3000);
    }

    hide() {
        if (!this.toast) return;

        this.toast.classList.remove('show');
        this.toast.classList.add('hide');

        // Remove hide class after animation
        setTimeout(() => {
            this.toast.classList.remove('hide');
        }, 300);

        clearTimeout(this.hideTimeout);
    }

    attachHandlers() {
        // Find all elements with data-coming-soon attribute
        const comingSoonElements = document.querySelectorAll('[data-coming-soon]');
        
        comingSoonElements.forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                
                const customMessage = element.getAttribute('data-coming-soon');
                const featureName = element.getAttribute('data-feature-name');
                
                let message = customMessage || 'This feature is currently under development.';
                let title = featureName ? `${featureName} - Coming Soon!` : 'Coming Soon!';
                
                this.show(message, title);
            });
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.comingSoonNotification = new ComingSoonNotification();
});

// Global function for easy access
function showComingSoon(message, title) {
    if (window.comingSoonNotification) {
        window.comingSoonNotification.show(message, title);
    }
}
