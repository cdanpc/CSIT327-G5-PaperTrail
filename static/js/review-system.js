/**
 * Unified Review System
 * Handles review creation, display, editing, and deletion across all content types
 */

class ReviewSystem {
    constructor(options = {}) {
        this.contentTypeId = options.contentTypeId;
        this.objectId = options.objectId;
        this.formSelector = options.formSelector || '#review-form';
        this.listSelector = options.listSelector || '#reviews-list';
        this.aggregateSelector = options.aggregateSelector || '#review-aggregate';
        this.userReviewSelector = options.userReviewSelector || '#user-review';
        
        this.form = document.querySelector(this.formSelector);
        this.list = document.querySelector(this.listSelector);
        this.aggregate = document.querySelector(this.aggregateSelector);
        this.userReviewContainer = document.querySelector(this.userReviewSelector);
        
        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Load reviews on initialization
        this.loadReviews();
        this.loadUserReview();
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const rating = formData.get('rating');
        const reviewText = formData.get('review_text');
        
        if (!rating) {
            this.showAlert('Please select a rating', 'warning');
            return;
        }
        
        // Show loading state
        const submitBtn = this.form.querySelector('[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        try {
            const response = await fetch('/reviews/create-or-update/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new FormData(this.form)
            });
            
            // Add hidden fields for AJAX request
            const formDataAjax = new FormData();
            formDataAjax.append('rating', rating);
            formDataAjax.append('review_text', reviewText || '');
            formDataAjax.append('content_type_id', this.contentTypeId);
            formDataAjax.append('object_id', this.objectId);
            
            const response2 = await fetch('/reviews/create-or-update/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formDataAjax
            });
            
            const data = await response2.json();
            
            if (data.success) {
                this.showAlert(data.message, 'success');
                
                // Reset form
                this.form.reset();
                
                // Reload reviews and user review
                await this.loadReviews();
                await this.loadUserReview();
                
                // Update aggregate display
                this.updateAggregate(data.aggregate);
            } else {
                this.showAlert(data.error || 'Failed to submit review', 'danger');
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            this.showAlert('An error occurred. Please try again.', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async loadReviews() {
        try {
            const response = await fetch(
                `/reviews/list/${this.contentTypeId}/${this.objectId}/`
            );
            const data = await response.json();
            
            if (data.success) {
                this.displayReviews(data.reviews, data.aggregate);
                this.updateAggregate(data.aggregate);
            }
        } catch (error) {
            console.error('Error loading reviews:', error);
        }
    }

    async loadUserReview() {
        try {
            const response = await fetch(
                `/reviews/user/${this.contentTypeId}/${this.objectId}/`
            );
            const data = await response.json();
            
            if (data.success && data.review) {
                this.displayUserReview(data.review);
            }
        } catch (error) {
            console.error('Error loading user review:', error);
        }
    }

    displayReviews(reviews, aggregate) {
        if (!this.list) return;
        
        this.list.innerHTML = '';
        
        if (reviews.length === 0) {
            this.list.innerHTML = '<p class="text-muted">No reviews yet. Be the first to share your experience!</p>';
            return;
        }
        
        reviews.forEach(review => {
            const reviewEl = this.createReviewElement(review);
            this.list.appendChild(reviewEl);
        });
    }

    createReviewElement(review) {
        const div = document.createElement('div');
        div.className = 'review-item card mb-3';
        div.dataset.reviewId = review.id;
        
        const starRating = this.createStarRating(review.rating);
        const isOwner = review.is_owner;
        
        div.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title mb-1">${this.escapeHtml(review.user)}</h6>
                        <small class="text-muted">${this.formatDate(review.created_at)}</small>
                    </div>
                    ${isOwner ? `
                        <button class="btn btn-sm btn-outline-danger delete-review-btn" data-review-id="${review.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
                <div class="mt-2 mb-2">${starRating}</div>
                ${review.review_text ? `<p class="card-text mt-2">${this.escapeHtml(review.review_text)}</p>` : ''}
            </div>
        `;
        
        // Attach delete handler
        if (isOwner) {
            const deleteBtn = div.querySelector('.delete-review-btn');
            deleteBtn.addEventListener('click', () => this.deleteReview(review.id));
        }
        
        return div;
    }

    displayUserReview(review) {
        if (!this.userReviewContainer) return;
        
        this.userReviewContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <strong>Your Review:</strong> ${review.rating} stars
                ${review.review_text ? `<p class="mt-2">${this.escapeHtml(review.review_text)}</p>` : ''}
                <small class="text-muted d-block mt-2">Reviewed on ${this.formatDate(review.created_at)}</small>
            </div>
        `;
    }

    updateAggregate(aggregate) {
        if (!this.aggregate) return;
        
        const { average_rating, total_reviews, rating_distribution } = aggregate;
        
        this.aggregate.innerHTML = `
            <div class="aggregate-rating mb-3">
                <div class="avg-stars mb-2">
                    ${this.createStarRating(average_rating)}
                    <span class="ms-2"><strong>${average_rating.toFixed(1)}</strong> / 5</span>
                </div>
                <small class="text-muted">${total_reviews} ${total_reviews === 1 ? 'review' : 'reviews'}</small>
            </div>
            ${total_reviews > 0 ? this.createRatingDistribution(rating_distribution) : ''}
        `;
    }

    createRatingDistribution(distribution) {
        let html = '<div class="rating-distribution mt-3">';
        
        for (let i = 5; i >= 1; i--) {
            const count = distribution[i] || 0;
            const percentage = distribution['5'] + distribution['4'] + distribution['3'] + distribution['2'] + distribution['1'] > 0
                ? Math.round((count / (distribution['5'] + distribution['4'] + distribution['3'] + distribution['2'] + distribution['1'])) * 100)
                : 0;
            
            html += `
                <div class="rating-bar mb-2">
                    <small>${i} <i class="fas fa-star" style="color: #ffc107;"></i></small>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar" style="width: ${percentage}%"></div>
                    </div>
                    <small>${count}</small>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    createStarRating(rating) {
        let html = '<span class="star-display">';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.floor(rating)) {
                html += '<i class="fas fa-star" style="color: #ffc107;"></i>';
            } else if (i - rating < 1 && i - rating > 0) {
                html += '<i class="fas fa-star-half-alt" style="color: #ffc107;"></i>';
            } else {
                html += '<i class="far fa-star" style="color: #ccc;"></i>';
            }
        }
        html += '</span>';
        return html;
    }

    async deleteReview(reviewId) {
        if (!confirm('Are you sure you want to delete your review?')) {
            return;
        }
        
        try {
            const response = await fetch(`/reviews/delete/?review_id=${reviewId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Review deleted successfully!', 'success');
                
                // Remove from DOM
                const reviewEl = document.querySelector(`[data-review-id="${reviewId}"]`);
                if (reviewEl) {
                    reviewEl.remove();
                }
                
                // Reload reviews
                await this.loadReviews();
                await this.loadUserReview();
                
                // Update aggregate
                this.updateAggregate(data.aggregate);
            } else {
                this.showAlert(data.error || 'Failed to delete review', 'danger');
            }
        } catch (error) {
            console.error('Error deleting review:', error);
            this.showAlert('An error occurred. Please try again.', 'danger');
        }
    }

    getCsrfToken() {
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

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.style.minWidth = '300px';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReviewSystem;
}
