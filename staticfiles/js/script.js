// Show popup for features in progress (generic)
function showFeatureInProgressPopup() {
    const toastEl = document.getElementById('featureToast');
    if (toastEl) {
        const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
        toast.show();
    }
}

// Show popup for features in progress with dynamic label/title/body
function showFeatureInProgressToast(sourceEl) {
    const toastEl = document.getElementById('featureToast');
    const titleEl = document.getElementById('featureToastTitle');
    const bodyEl = document.getElementById('featureToastBody');
    if (!toastEl || !titleEl || !bodyEl) return;

    const explicitLabel = sourceEl && sourceEl.getAttribute('data-feature-label');
    const progressLabel = sourceEl && sourceEl.getAttribute('data-feature-in-progress');
    const textLabel = sourceEl && sourceEl.textContent;

    const formatLabel = (rawValue, fallback) => {
        if (!rawValue) return fallback || 'This';
        return rawValue
            .trim()
            .replace(/[-_]+/g, ' ')
            .replace(/\s+/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    };

    const chosenLabel = explicitLabel || progressLabel || textLabel || 'This';
    const formatted = formatLabel(chosenLabel, 'This');
    titleEl.textContent = `${formatted} Feature`;
    bodyEl.textContent = `${formatted} is currently in progress. Thanks for checking in!`;

    bootstrap.Toast.getOrCreateInstance(toastEl, { autohide: true, delay: 4000 }).show();
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

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Dashboard] DOMContentLoaded fired');
    
    // Ensure Bootstrap toast is initialized
    const toastEl = document.getElementById('featureToast');
    if (toastEl) {
        bootstrap.Toast.getOrCreateInstance(toastEl);
    }

    // Initialize all tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });

    // Show Django message toasts if present
    document.querySelectorAll('.toast-message').forEach(toastElement => {
        bootstrap.Toast.getOrCreateInstance(toastElement, {
            animation: true,
            autohide: true,
            delay: 5000
        }).show();
    });
    
    // --- Greeting Message Logic ---
    function setGreeting() {
        const greetingElement = document.getElementById('greetingMessage');
        if (!greetingElement) return;
        
        // Extract username from existing text or data attribute
        let userName = greetingElement.getAttribute('data-username');
        if (!userName) {
            userName = greetingElement.textContent.replace(/Good (morning|afternoon|evening|day), /, '').replace('!', '');
        }
        
        // Get Philippines time (UTC+8)
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const phTime = new Date(utc + (3600000 * 8));
        const hour = phTime.getHours();
        
        let greeting;
        if (hour >= 5 && hour < 12) {
            greeting = 'Good morning';
        } else if (hour >= 12 && hour < 18) {
            greeting = 'Good afternoon';
        } else {
            greeting = 'Good evening';
        }
        
        greetingElement.textContent = greeting + ', ' + userName + '!';
    }
    setGreeting();

    // Global search: focus with '/' (when not typing in an input/textarea)
    const searchInput = document.querySelector('.search-box-inline input, .search-box input');
    if (searchInput) {
        searchInput.setAttribute('aria-label', 'Global search');
    }
    const bellButton = document.querySelector('.icon-btn');
    if (bellButton) {
        bellButton.setAttribute('aria-label', 'Notifications');
        bellButton.setAttribute('title', 'Notifications');
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const activeTag = (document.activeElement && document.activeElement.tagName || '').toLowerCase();
            if (activeTag !== 'input' && activeTag !== 'textarea' && searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        }
    });

    // Toast notifications for coming-soon/in-progress features
    document.querySelectorAll('[data-feature="coming-soon"], [data-feature="in-progress"], [data-feature-in-progress]')
        .forEach(function(element) {
            element.addEventListener('click', function(e) {
                e.preventDefault();
                // Prefer dynamic toast if we have labels, else generic
                if (element.hasAttribute('data-feature-in-progress') || element.hasAttribute('data-feature-label')) {
                    showFeatureInProgressToast(element);
                } else {
                    showFeatureInProgressPopup();
                }
            });
            element.classList.add('feature-link');
        });

    // Navbar scroll effect (used on landing and app pages)
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const applyNavbarScroll = () => {
            if (window.scrollY > 50) navbar.classList.add('scrolled');
            else navbar.classList.remove('scrolled');
        };
        window.addEventListener('scroll', applyNavbarScroll);
        applyNavbarScroll();
    }

    // Smooth scroll for landing page nav/footer links
    if (document.querySelector('.navbar-landing') || document.querySelector('.hero-section')) {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link[href^="#"]');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (!href || !href.startsWith('#')) return;
                e.preventDefault();
                const targetId = href.substring(1);
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    navLinks.forEach(l => l.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });

        const sections = document.querySelectorAll('section[id]');
        const highlightNavOnScroll = () => {
            const scrollY = window.pageYOffset;
            sections.forEach(section => {
                const sectionHeight = section.offsetHeight;
                const sectionTop = section.offsetTop - 100;
                const sectionId = section.getAttribute('id');
                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${sectionId}`) link.classList.add('active');
                    });
                }
            });
        };
        window.addEventListener('scroll', highlightNavOnScroll);

        // Footer smooth links
        document.querySelectorAll('.footer-scroll-link[href^="#"]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                if (targetSection) targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }

    // ==========================================
    // LANDING PAGE ANIMATIONS - Phase 1
    // ==========================================
    
    // 1. Scroll-triggered animations for feature cards and team cards
    const observeElements = document.querySelectorAll('.feature-card, .team-card');
    if (observeElements.length > 0) {
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Add stagger effect for feature cards
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 100); // 100ms delay between each card
                    
                    scrollObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px'
        });
        
        observeElements.forEach(el => scrollObserver.observe(el));
    }
    
    // 2. Animated stat counter
    const statNumbers = document.querySelectorAll('.stat-number');
    let statsAnimated = false;
    
    if (statNumbers.length > 0) {
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !statsAnimated) {
                    statsAnimated = true;
                    
                    statNumbers.forEach(stat => {
                        const target = parseInt(stat.getAttribute('data-target')) || 
                                     parseInt(stat.textContent.replace(/[^0-9]/g, '')) || 0;
                        const duration = 2000; // 2 seconds
                        const increment = target / (duration / 16); // 60fps
                        let current = 0;
                        
                        const updateCount = () => {
                            current += increment;
                            if (current < target) {
                                stat.textContent = Math.floor(current).toLocaleString();
                                requestAnimationFrame(updateCount);
                            } else {
                                stat.textContent = target.toLocaleString();
                            }
                        };
                        updateCount();
                    });
                    
                    statsObserver.disconnect();
                }
            });
        }, {
            threshold: 0.5
        });
        
        // Observe the first stat card to trigger all counters
        const firstStatCard = document.querySelector('.stat-card');
        if (firstStatCard) {
            statsObserver.observe(firstStatCard);
        }
    }
    
    // ==========================================
    // PHASE 2 ENHANCEMENTS
    // ==========================================
    
    // 3. Magnetic Button Effect
    const magneticButtons = document.querySelectorAll('.hero-cta .btn-primary');
    magneticButtons.forEach(button => {
        button.addEventListener('mousemove', (e) => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            // Limit the movement to 10px max
            const moveX = (x / rect.width) * 20;
            const moveY = (y / rect.height) * 20;
            
            button.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translate(0, 0)';
        });
    });
    
    // 4. Scroll Progress Indicator
    const createScrollProgress = () => {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.innerHTML = '<div class="scroll-progress-bar"></div>';
        document.body.appendChild(progressBar);
        
        const progressBarFill = progressBar.querySelector('.scroll-progress-bar');
        
        window.addEventListener('scroll', () => {
            const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (window.scrollY / windowHeight) * 100;
            progressBarFill.style.width = scrolled + '%';
        });
    };
    
    // Only create on landing page
    if (document.querySelector('.hero-section')) {
        createScrollProgress();
    }
    
    // ==========================================
    // PHASE 3 ENHANCEMENTS
    // ==========================================
    
    // 5. Parallax Background Effect
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        const parallaxBg = heroSection.querySelector('::before');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const heroHeight = heroSection.offsetHeight;
            
            // Only apply parallax while hero is visible
            if (scrolled < heroHeight) {
                const parallaxSpeed = 0.5;
                heroSection.style.setProperty('--parallax-offset', `${scrolled * parallaxSpeed}px`);
            }
        });
    }
    
    // 6. 3D Card Tilt Effect
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -10; // Max 10deg
            const rotateY = ((x - centerX) / centerX) * 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
        });
    });
    
    // 7. Typing Animation for Hero Subtitle
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle && !heroSubtitle.dataset.typed) {
        const originalText = heroSubtitle.textContent;
        const lines = originalText.split('\n').map(line => line.trim()).filter(line => line);
        
        heroSubtitle.textContent = '';
        heroSubtitle.dataset.typed = 'true';
        
        let lineIndex = 0;
        let charIndex = 0;
        
        const typeWriter = () => {
            if (lineIndex < lines.length) {
                const currentLine = lines[lineIndex];
                
                if (charIndex < currentLine.length) {
                    if (charIndex === 0 && lineIndex > 0) {
                        heroSubtitle.innerHTML += '<br>';
                    }
                    
                    heroSubtitle.innerHTML = heroSubtitle.innerHTML.replace('<span class="typing-cursor"></span>', '');
                    heroSubtitle.innerHTML += currentLine.charAt(charIndex);
                    heroSubtitle.innerHTML += '<span class="typing-cursor"></span>';
                    
                    charIndex++;
                    setTimeout(typeWriter, 30); // 30ms per character
                } else {
                    charIndex = 0;
                    lineIndex++;
                    setTimeout(typeWriter, 200); // 200ms pause between lines
                }
            } else {
                // Remove cursor after typing completes
                setTimeout(() => {
                    const cursor = heroSubtitle.querySelector('.typing-cursor');
                    if (cursor) cursor.remove();
                }, 2000);
            }
        };
        
        // Start typing after a short delay
        setTimeout(typeWriter, 500);
    }
    
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
    // Resource upload: Client-side dynamic formset logic — only initialize if present
    const formsetContainer = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form-btn');
    const totalFormsInput = document.querySelector('[name="related_links-TOTAL_FORMS"]');

    if (formsetContainer && totalFormsInput) {
        let emptyFormTemplate = null;

        function updateFormIndex(element, index) {
            const prefix = 'related_links';
            const nameRegex = new RegExp(`${prefix}-\\d+`, 'g');
            ['name', 'id', 'htmlFor'].forEach(attr => {
                if (element.hasAttribute(attr)) {
                    const currentValue = element.getAttribute(attr);
                    if (currentValue) element.setAttribute(attr, currentValue.replace(nameRegex, `${prefix}-${index}`));
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
                    const header = form.querySelector('h6.text-primary');
                    if (header) header.textContent = `Link #${visibleCount + 1}`;
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
            const currentFormCount = parseInt(totalFormsInput.value);
            const newForm = emptyFormTemplate.cloneNode(true);
            newForm.style.display = 'block';
            newForm.id = `related-form-${currentFormCount}`;
            newForm.querySelectorAll('[name^="related_links-"], [id^="id_related_links-"], label[for^="id_related_links-"]').forEach(element => {
                updateFormIndex(element, currentFormCount);
                if (element.name && element.name.endsWith('-id')) element.value = '';
            });
            formsetContainer.appendChild(newForm);
            totalFormsInput.value = currentFormCount + 1;
            attachDeleteHandler(newForm);
            reIndexForms();
        }

        // Initialization
        const currentForms = formsetContainer.querySelectorAll('.related-link-form');
        if (currentForms.length > 0) {
            const lastForm = currentForms[currentForms.length - 1];
            emptyFormTemplate = lastForm.cloneNode(true);
            emptyFormTemplate.querySelectorAll('input, select, textarea').forEach(element => {
                if (element.type !== 'hidden' && element.type !== 'checkbox') element.value = '';
                if (element.name && element.name.endsWith('-DELETE')) element.checked = false;
                if (element.name && element.name.endsWith('-id')) element.value = '';
            });
            emptyFormTemplate.style.display = 'none';
            emptyFormTemplate.id = 'empty-form-template';
            formsetContainer.appendChild(emptyFormTemplate);
        }

        currentForms.forEach((form) => {
            const pkInput = form.querySelector('input[name$="-id"]');
            if (!pkInput || !pkInput.value) form.style.display = 'none';
            attachDeleteHandler(form);
        });

        reIndexForms();
        if (addButton) addButton.addEventListener('click', addForm);
    }

});