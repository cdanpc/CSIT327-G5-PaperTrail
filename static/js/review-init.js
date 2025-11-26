/**
 * Review System Initialization
 * Initializes ReviewSystem, StarRating, and average rating components
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ReviewSystem for review_list.html components
    const reviewSystems = document.querySelectorAll('[data-review-content-type][data-review-object-id]');
    
    reviewSystems.forEach(function(element) {
        const contentTypeId = parseInt(element.getAttribute('data-review-content-type'));
        const objectId = parseInt(element.getAttribute('data-review-object-id'));
        
        // Initialize ReviewSystem
        if (typeof ReviewSystem !== 'undefined') {
            const reviewSystem = new ReviewSystem({
                contentTypeId: contentTypeId,
                objectId: objectId,
                formSelector: '#review-form',
                listSelector: '#reviews-list',
                aggregateSelector: '#review-aggregate',
                userReviewSelector: '#user-review'
            });
        }
    });
    
    // Initialize StarRating components
    const starRatings = document.querySelectorAll('.star-rating');
    starRatings.forEach(function(ratingDiv) {
        if (typeof StarRating !== 'undefined') {
            const ratingId = ratingDiv.getAttribute('data-rating-id');
            const starRating = new StarRating(ratingDiv);
            
            // Sync with hidden input if it exists
            if (ratingId) {
                ratingDiv.addEventListener('rating-changed', function(e) {
                    const input = document.getElementById(ratingId);
                    if (input) {
                        input.value = e.detail.rating;
                    }
                });
            }
        }
    });
    
    // Initialize average rating displays
    const averageRatings = document.querySelectorAll('[data-review-content-type][data-review-object-id].average-rating > div');
    averageRatings.forEach(function(container) {
        const contentTypeId = container.getAttribute('data-review-content-type');
        const objectId = container.getAttribute('data-review-object-id');
        
        if (contentTypeId && objectId && container.classList.contains('loading')) {
            loadAverageRating(container, contentTypeId, objectId);
        }
    });
});

/**
 * Load and display average rating
 */
async function loadAverageRating(container, contentTypeId, objectId) {
    try {
        const response = await fetch(`/reviews/list/${contentTypeId}/${objectId}/?limit=1`);
        const data = await response.json();
        
        if (data.success && data.aggregate) {
            const agg = data.aggregate;
            
            let starsHtml = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= Math.floor(agg.average_rating)) {
                    starsHtml += '<i class="fas fa-star" style="color: #ffc107;"></i>';
                } else if (i - agg.average_rating < 1 && i - agg.average_rating > 0) {
                    starsHtml += '<i class="fas fa-star-half-alt" style="color: #ffc107;"></i>';
                } else {
                    starsHtml += '<i class="far fa-star" style="color: #ccc;"></i>';
                }
            }
            
            container.innerHTML = `
                <div class="d-flex align-items-center gap-2">
                    <span class="stars">${starsHtml}</span>
                    <span class="rating-value"><strong>${agg.average_rating.toFixed(1)}</strong>/5</span>
                    <span class="rating-count text-muted">(<small>${agg.total_reviews} review${agg.total_reviews !== 1 ? 's' : ''}</small>)</span>
                </div>
            `;
            container.classList.remove('loading');
        }
    } catch (error) {
        console.error('Error loading average rating:', error);
        container.innerHTML = '<p class="text-danger">Error loading rating</p>';
        container.classList.remove('loading');
    }
}

