// Show popup for features in progress
function showFeatureInProgressPopup() {
    const popup = document.createElement('div');
    popup.className = 'feature-popup';
    popup.innerHTML = `
        <div class="feature-popup-content">
            <h4>Feature Coming Soon!</h4>
            <p>This feature is currently under development. We're working hard to bring it to you soon!</p>
            <button class="btn btn-primary" onclick="this.parentElement.parentElement.remove()">Got it!</button>
        </div>
    `;
    document.body.appendChild(popup);

    // Add fade-in animation
    setTimeout(() => popup.classList.add('show'), 10);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => popup.remove(), 300);
    }, 5000);
}

// Password strength meter
function updatePasswordStrength(password) {
    const strengthMeter = document.querySelector('.password-strength-meter');
    if (!strengthMeter) return;

    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    strengthMeter.className = 'password-strength-meter';
    switch(strength) {
        case 0:
        case 1:
            strengthMeter.classList.add('weak');
            break;
        case 2:
        case 3:
            strengthMeter.classList.add('medium');
            break;
        case 4:
        case 5:
            strengthMeter.classList.add('strong');
            break;
    }
}

// Dashboard functionality
const Dashboard = {
    // Initialize dashboard features
    init() {
        this.initializeTooltips();
        this.initializePopovers();
        this.setupScrollAnimations();
        this.initializeCharts();
        this.animateStats();
        this.setupResponsiveCards();
        this.setupNotifications();
    },

    // Initialize Bootstrap tooltips
    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    },

    // Initialize Bootstrap popovers
    initializePopovers() {
        const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
        popovers.forEach(popover => {
            new bootstrap.Popover(popover);
        });
    },

    // Setup scroll animations for dashboard elements
    setupScrollAnimations() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, { threshold: 0.1 });

        elements.forEach(element => {
            observer.observe(element);
        });
    },

    // Animate statistics with counting effect
    animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        stats.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target'));
            if (isNaN(target)) return;

            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const animate = () => {
                current += increment;
                if (current < target) {
                    stat.textContent = Math.round(current).toLocaleString();
                    requestAnimationFrame(animate);
                } else {
                    stat.textContent = target.toLocaleString();
                }
            };
            animate();
        });
    },

    // Setup responsive card heights
    setupResponsiveCards() {
        const equalizeCardHeights = () => {
            const cardGroups = document.querySelectorAll('.card-group-equal-height');
            cardGroups.forEach(group => {
                const cards = group.querySelectorAll('.card');
                let maxHeight = 0;
                
                // Reset heights
                cards.forEach(card => card.style.height = 'auto');
                
                // Find max height
                cards.forEach(card => {
                    maxHeight = Math.max(maxHeight, card.offsetHeight);
                });
                
                // Set equal heights
                cards.forEach(card => card.style.height = maxHeight + 'px');
            });
        };

        // Run on load and resize
        window.addEventListener('load', equalizeCardHeights);
        window.addEventListener('resize', debounce(equalizeCardHeights, 250));
    },

    // Initialize charts if they exist
    initializeCharts() {
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') return;

        // Setup charts as needed
        const chartElements = document.querySelectorAll('[data-chart]');
        chartElements.forEach(element => {
            const type = element.dataset.chartType;
            const data = JSON.parse(element.dataset.chartData);
            
            new Chart(element, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        });
    },

    // Setup notification system
    setupNotifications() {
        const notificationBadge = document.querySelector('.notification-badge');
        const notificationsList = document.querySelector('.notifications-list');

        if (notificationBadge && notificationsList) {
            // Update notifications (example)
            this.updateNotifications();

            // Setup polling for new notifications
            setInterval(() => this.updateNotifications(), 60000);
        }
    },

    // Update notifications (example implementation)
    updateNotifications() {
        // This would typically fetch from your backend
        console.log('Checking for new notifications...');
    }
};

// Utility function for debouncing
function debounce(func, wait) {
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

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});

document.addEventListener('DOMContentLoaded', function() {
    
    // PART 1: Conditional Field Display
    const typeSelect = document.getElementById('id_resource_type'); 
    const fileContainer = document.getElementById('file-upload-container');
    const linkContainer = document.getElementById('link-upload-container');
    const fileGuidelines = document.getElementById('file-guidelines');
    const linkGuidelines = document.getElementById('link-guidelines');
    const initialGuidelines = document.getElementById('initial-guidelines');

    function toggleFields(selectedType) {
        fileContainer.style.display = 'none';
        linkContainer.style.display = 'none';
        fileGuidelines.style.display = 'none';
        linkGuidelines.style.display = 'none';
        initialGuidelines.style.display = 'block';

        if (selectedType === 'file') {
            fileContainer.style.display = 'block';
            fileGuidelines.style.display = 'block';
            initialGuidelines.style.display = 'none';
        } else if (selectedType === 'link') {
            linkContainer.style.display = 'block';
            linkGuidelines.style.display = 'block';
            initialGuidelines.style.display = 'none';
        }
    }
    
    if (typeSelect) {
        toggleFields(typeSelect.value);
        typeSelect.addEventListener('change', function() {
            toggleFields(this.value);
        });
    }

    // PART 2: Client-Side Dynamic Formset Logic (Related Resources)
    const formsetContainer = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form-btn');
    const totalFormsInput = document.querySelector('[name="related_links-TOTAL_FORMS"]'); 
    
    let emptyFormTemplate = null;

    function updateFormIndex(element, index) {
        const prefix = 'related_links';
        const nameRegex = new RegExp(`${prefix}-\\d+`, 'g'); 
        
        ['name', 'id', 'htmlFor'].forEach(attr => {
            if (element.hasAttribute(attr)) {
                let currentValue = element.getAttribute(attr);
                if (currentValue) {
                    element.setAttribute(attr, currentValue.replace(nameRegex, `${prefix}-${index}`));
                }
            }
        });
    }
    
    function reIndexForms() {
        const forms = formsetContainer.querySelectorAll('.related-link-form');
        let formIndex = 0;      
        let visibleCount = 0;   
        
        forms.forEach((form) => {
            if (form.id === 'empty-form-template') return; 

            const deleteCheckbox = form.querySelector('input[name$="-DELETE"]');
            
            const isVisible = form.style.display !== 'none' && (!deleteCheckbox || !deleteCheckbox.checked);

            form.querySelectorAll('[name^="related_links-"], [id^="id_related_links-"], label[for^="id_related_links-"]').forEach(element => {
                updateFormIndex(element, formIndex);
            });
            
            if (isVisible) {
                let header = form.querySelector('h6.text-primary');
                if (header) {
                    header.textContent = `Link #${visibleCount + 1}`;
                }
                visibleCount++;
            }
            formIndex++; 
        });
        
        totalFormsInput.value = formIndex; 
    }

    function deleteForm(e) {
        e.preventDefault();
        const formToDelete = e.target.closest('.related-link-form');
        if (!formToDelete || formToDelete.id === 'empty-form-template') return;

        const pkInput = formToDelete.querySelector('input[name$="-id"]');
        const deleteCheckbox = formToDelete.querySelector('input[name$="-DELETE"]');

        if (deleteCheckbox && pkInput && pkInput.value) {
            deleteCheckbox.checked = true;
            formToDelete.style.display = 'none';
        } else {
            formToDelete.remove();
        }
        
        reIndexForms(); 
    }
    
    function attachDeleteHandler(form) {
        const deleteButton = form.querySelector('.remove-form-btn');
        if (deleteButton) {
            deleteButton.removeEventListener('click', deleteForm);
            deleteButton.addEventListener('click', deleteForm);
        }
    }
    
    function addForm(e) {
        e.preventDefault();
        if (!emptyFormTemplate) return;
    
        let currentFormCount = parseInt(totalFormsInput.value);
        const newForm = emptyFormTemplate.cloneNode(true);
        
        newForm.style.display = 'block';
        newForm.id = `related-form-${currentFormCount}`;
        
        // CRITICAL FIX: Only index elements with the related_links prefix
        // when setting up the new form. This prevents polluting the Tags field.
        newForm.querySelectorAll('[name^="related_links-"], [id^="id_related_links-"], label[for^="id_related_links-"]').forEach(element => {
            updateFormIndex(element, currentFormCount);
            
            // This part is crucial for new forms: reset the PK
            if (element.name && element.name.endsWith('-id')) {
                element.value = '';
            }
        });
    
        formsetContainer.appendChild(newForm);
        totalFormsInput.value = currentFormCount + 1; 
        
        attachDeleteHandler(newForm);
        
        // Global re-index to confirm numbering and total forms count
        reIndexForms();
    }

    // Initialization
    const currentForms = formsetContainer.querySelectorAll('.related-link-form');
    
    // Create and hide the empty form template for cloning
    if (currentForms.length > 0) {
        const lastForm = currentForms[currentForms.length - 1]; 
        
        emptyFormTemplate = lastForm.cloneNode(true);
        
        emptyFormTemplate.querySelectorAll('input, select, textarea').forEach(element => {
            if (element.type !== 'hidden' && element.type !== 'checkbox') {
                element.value = '';
            }
            if (element.name && element.name.endsWith('-DELETE')) {
                element.checked = false;
            }
            if (element.name && element.name.endsWith('-id')) {
                element.value = '';
            }
        });
        
        emptyFormTemplate.style.display = 'none';
        emptyFormTemplate.id = 'empty-form-template';
        
        formsetContainer.appendChild(emptyFormTemplate);
    }
    
    // Hide initial empty form(s) and attach handlers
    currentForms.forEach((form) => {
        const pkInput = form.querySelector('input[name$="-id"]');
        
        if (!pkInput || !pkInput.value) {
            form.style.display = 'none';
        }
        
        attachDeleteHandler(form);
    });
    
    reIndexForms();

    if (addButton) {
        addButton.addEventListener('click', addForm);
    }
});