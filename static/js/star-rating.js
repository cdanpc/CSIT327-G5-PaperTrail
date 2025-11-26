/**
 * Unified Star Rating Component
 * Handles interactive 5-star rating with hover effects, keyboard support, and accessibility
 * 
 * Usage:
 * <div class="star-rating" data-rating-id="form-rating-input"></div>
 * Or for display-only:
 * <div class="star-rating-display" data-rating="3.5"></div>
 */

class StarRating {
    constructor(container) {
        this.container = container;
        this.isInteractive = !container.classList.contains('star-rating-display');
        this.rating = parseFloat(container.dataset.rating) || 0;
        this.init();
    }

    init() {
        if (this.isInteractive) {
            this.initInteractive();
        } else {
            this.initDisplay();
        }
    }

    initInteractive() {
        // Create star elements with proper ARIA labels
        this.container.innerHTML = '';
        this.container.setAttribute('role', 'radiogroup');
        this.container.setAttribute('aria-label', 'Star rating');
        
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('button');
            star.type = 'button';
            star.className = 'star-btn';
            star.dataset.value = i;
            star.setAttribute('aria-label', `${i} star${i > 1 ? 's' : ''}`);
            star.setAttribute('role', 'radio');
            star.setAttribute('aria-checked', this.rating === i);
            
            star.innerHTML = '<i class="fas fa-star"></i>';
            
            // Events
            star.addEventListener('click', () => this.selectRating(i));
            star.addEventListener('mouseenter', () => this.showHover(i));
            star.addEventListener('mouseleave', () => this.showCurrent());
            star.addEventListener('keydown', (e) => this.handleKeydown(e, i));
            
            this.container.appendChild(star);
        }

        // Find hidden input for storing value
        const inputId = this.container.dataset.ratingId;
        if (inputId) {
            this.input = document.getElementById(inputId);
        }

        // Set initial state
        this.showCurrent();
    }

    initDisplay() {
        // Display-only rating - no interaction
        this.container.innerHTML = '';
        const rating = parseFloat(this.container.dataset.rating) || 0;

        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('span');
            star.className = 'star-display';
            
            if (i <= Math.floor(rating)) {
                star.classList.add('filled');
            } else if (i - rating < 1 && i - rating > 0) {
                star.classList.add('half-filled');
            }
            
            star.innerHTML = '<i class="fas fa-star"></i>';
            this.container.appendChild(star);
        }

        // Add rating text
        if (rating > 0) {
            const text = document.createElement('span');
            text.className = 'rating-text';
            text.textContent = `${rating.toFixed(1)}`;
            this.container.appendChild(text);
        }
    }

    selectRating(value) {
        this.rating = value;
        
        // Update hidden input if exists
        if (this.input) {
            this.input.value = value;
            this.input.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // Update display
        this.showCurrent();
        
        // Trigger custom event for external handlers
        this.container.dispatchEvent(new CustomEvent('rating-changed', {
            detail: { rating: value }
        }));
    }

    showHover(hoveredValue) {
        const stars = this.container.querySelectorAll('.star-btn');
        stars.forEach((star, index) => {
            if (index + 1 <= hoveredValue) {
                star.classList.add('hovered');
                star.classList.remove('selected');
            } else {
                star.classList.remove('hovered');
            }
        });
    }

    showCurrent() {
        const stars = this.container.querySelectorAll('.star-btn');
        stars.forEach((star, index) => {
            const value = index + 1;
            
            if (value <= this.rating) {
                star.classList.add('selected');
                star.classList.remove('hovered');
            } else {
                star.classList.remove('selected', 'hovered');
            }
            
            // Update ARIA attributes
            star.setAttribute('aria-checked', value === this.rating);
        });
    }

    handleKeydown(e, value) {
        let newValue = value;
        
        if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
            e.preventDefault();
            newValue = Math.min(value + 1, 5);
            const nextStar = this.container.querySelector(`[data-value="${newValue}"]`);
            if (nextStar) nextStar.focus();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
            e.preventDefault();
            newValue = Math.max(value - 1, 1);
            const prevStar = this.container.querySelector(`[data-value="${newValue}"]`);
            if (prevStar) prevStar.focus();
        } else if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.selectRating(value);
            return;
        }
        
        if (newValue !== value) {
            this.selectRating(newValue);
        }
    }

    getRating() {
        return this.rating;
    }

    setRating(value) {
        if (value >= 1 && value <= 5) {
            this.selectRating(value);
        }
    }
}

// Auto-initialize all star ratings on page load
document.addEventListener('DOMContentLoaded', function() {
    const ratingContainers = document.querySelectorAll('.star-rating, .star-rating-display');
    ratingContainers.forEach(container => {
        new StarRating(container);
    });
});

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StarRating;
}
