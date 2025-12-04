// Quiz Detail Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize rating modal
    initRatingModal();
    
    // Handle edit quiz form
    initEditQuizForm();
    
    // Handle like button
    const likeBtn = document.getElementById('likeBtn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            const likeUrl = this.dataset.likeUrl;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const isLiked = this.dataset.liked === 'true';
            
            fetch(likeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update button state
                const icon = this.querySelector('i');
                const span = this.querySelector('span');
                
                if (data.liked) {
                    icon.className = 'fas fa-heart';
                    span.textContent = 'Liked';
                    this.dataset.liked = 'true';
                } else {
                    icon.className = 'far fa-heart';
                    span.textContent = 'Like';
                    this.dataset.liked = 'false';
                }
                
                // Update like count in stats
                const likesStatValue = document.getElementById('likesStatValue');
                if (likesStatValue && data.like_count !== undefined) {
                    likesStatValue.textContent = data.like_count;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating like status');
            });
        });
    }
});

// Initialize rating modal (reuse from flashcard_detail.js logic)
function initRatingModal() {
    const ratingModal = document.getElementById('ratingModal');
    if (!ratingModal) return;
    
    const stars = ratingModal.querySelectorAll('.rating-star');
    const submitBtn = ratingModal.querySelector('#submitRating');
    const ratingMessage = ratingModal.querySelector('#ratingMessage');
    let selectedRating = 0;
    
    // Star hover and click effects
    stars.forEach(star => {
        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            highlightStars(rating);
        });
        
        star.addEventListener('click', function() {
            selectedRating = parseInt(this.dataset.rating);
            highlightStars(selectedRating);
            submitBtn.disabled = false;
            ratingMessage.textContent = `You selected ${selectedRating} star${selectedRating > 1 ? 's' : ''}`;
            ratingMessage.className = 'rating-message text-success';
        });
    });
    
    // Reset stars on mouse leave
    ratingModal.addEventListener('mouseleave', function() {
        if (selectedRating > 0) {
            highlightStars(selectedRating);
        } else {
            highlightStars(0);
        }
    });
    
    // Submit rating
    submitBtn.addEventListener('click', function() {
        const rateUrl = this.dataset.rateUrl;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        fetch(rateUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `stars=${selectedRating}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                ratingMessage.textContent = 'Rating submitted successfully!';
                ratingMessage.className = 'rating-message text-success';
                
                // Update rating display in stats box
                const ratingStatValue = document.querySelector('.stat-row:nth-child(2) .stat-value');
                if (ratingStatValue && data.new_average !== undefined) {
                    ratingStatValue.textContent = parseFloat(data.new_average).toFixed(1);
                }
                
                // Close modal after showing success message
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(ratingModal);
                    modal.hide();
                }, 800);
            } else {
                ratingMessage.textContent = data.message || 'Error submitting rating';
                ratingMessage.className = 'rating-message text-danger';
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit Rating';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            ratingMessage.textContent = 'Error submitting rating';
            ratingMessage.className = 'rating-message text-danger';
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Rating';
        });
    });
    
    // Reset modal when closed
    ratingModal.addEventListener('hidden.bs.modal', function() {
        selectedRating = 0;
        highlightStars(0);
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Submit Rating';
        ratingMessage.textContent = '';
    });
    
    function highlightStars(rating) {
        stars.forEach(star => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
}

// Initialize edit quiz form
function initEditQuizForm() {
    const editForm = document.getElementById('editQuizForm');
    if (!editForm) return;
    
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const quizId = this.dataset.quizId;
        const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
        const submitBtn = this.querySelector('button[type="submit"]');
        
        const formData = new FormData();
        formData.append('title', document.getElementById('editQuizTitle').value);
        formData.append('description', document.getElementById('editQuizDescription').value);
        formData.append('is_public', document.getElementById('editQuizVisibility').checked);
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        fetch(`/quizzes/${quizId}/edit/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update page content
                document.querySelector('.resource-title').textContent = data.title;
                const descElement = document.querySelector('.resource-description');
                if (data.description) {
                    descElement.textContent = data.description;
                    descElement.classList.remove('text-muted', 'fst-italic');
                } else {
                    descElement.textContent = 'No description provided.';
                    descElement.classList.add('text-muted', 'fst-italic');
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editQuizModal'));
                modal.hide();
                
                // Show success message
                alert('Quiz updated successfully!');
                
                // Reload page to reflect visibility changes
                if (data.visibility_changed) {
                    location.reload();
                }
            } else {
                alert(data.message || 'Error updating quiz');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save Changes';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating quiz');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Changes';
        });
    });
}
