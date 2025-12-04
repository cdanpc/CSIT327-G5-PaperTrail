// Flashcard Detail Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize rating modal
    initRatingModal();
    
    // Handle Edit Deck form submission
    initEditDeckForm();
    
    // Handle Add Card form submission
    const addCardForm = document.getElementById('addCardForm');
    if (addCardForm) {
        addCardForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const deckId = document.querySelector('[data-deck-id]').dataset.deckId;
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    // Close modal and reload page to show new card
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addCardModal'));
                    modal.hide();
                    window.location.reload();
                } else {
                    alert('Error adding card. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error adding card. Please try again.');
            });
        });
    }
    
    // Handle card deletion from preview modal
    document.querySelectorAll('.delete-card-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const cardId = this.dataset.cardId;
            const deleteUrl = this.dataset.deleteUrl;
            
            if (confirm('Are you sure you want to delete this card?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = deleteUrl;
                
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
    
    // Handle card editing from preview modal (inline editing)
    document.querySelectorAll('.edit-card-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const cardId = this.dataset.cardId;
            
            // Hide view mode, show edit mode
            document.querySelector(`.card-view-mode-${cardId}`).classList.add('d-none');
            document.querySelector(`.card-edit-mode-${cardId}`).classList.remove('d-none');
            
            // Close dropdown
            const dropdown = bootstrap.Dropdown.getInstance(document.getElementById(`cardDropdown${cardId}`));
            if (dropdown) dropdown.hide();
        });
    });
    
    // Handle cancel edit
    document.querySelectorAll('.cancel-edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const cardId = this.dataset.cardId;
            
            // Show view mode, hide edit mode
            document.querySelector(`.card-view-mode-${cardId}`).classList.remove('d-none');
            document.querySelector(`.card-edit-mode-${cardId}`).classList.add('d-none');
            
            // Reset textarea values to original
            const originalFront = document.getElementById(`cardFront${cardId}`).textContent;
            const originalBack = document.getElementById(`cardBack${cardId}`).textContent;
            document.querySelector(`.card-front-input-${cardId}`).value = originalFront;
            document.querySelector(`.card-back-input-${cardId}`).value = originalBack;
        });
    });
    
    // Handle save edit
    document.querySelectorAll('.save-edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const cardId = this.dataset.cardId;
            const updateUrl = this.dataset.updateUrl;
            const newFront = document.querySelector(`.card-front-input-${cardId}`).value.trim();
            const newBack = document.querySelector(`.card-back-input-${cardId}`).value.trim();
            
            if (!newFront || !newBack) {
                alert('Both front and back text are required!');
                return;
            }
            
            // Disable button during save
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    front_text: newFront,
                    back_text: newBack
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the displayed text in view mode
                    document.getElementById(`cardFront${cardId}`).textContent = newFront;
                    document.getElementById(`cardBack${cardId}`).textContent = newBack;
                    
                    // Update data attributes for future reference
                    const editBtn = document.querySelector(`.edit-card-btn[data-card-id="${cardId}"]`);
                    if (editBtn) {
                        editBtn.dataset.frontText = newFront;
                        editBtn.dataset.backText = newBack;
                    }
                    
                    // Switch back to view mode
                    document.querySelector(`.card-view-mode-${cardId}`).classList.remove('d-none');
                    document.querySelector(`.card-edit-mode-${cardId}`).classList.add('d-none');
                    
                    // Show success feedback
                    const cardItem = document.querySelector(`.card-item-${cardId}`);
                    cardItem.style.borderLeftColor = 'var(--color-success)';
                    setTimeout(() => {
                        cardItem.style.borderLeftColor = 'var(--color-secondary)';
                    }, 1500);
                } else {
                    alert('Error updating card: ' + (data.error || 'Unknown error'));
                }
                
                // Re-enable button
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-check"></i> Save';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating card. Please try again.');
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-check"></i> Save';
            });
        });
    });
    
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

// Initialize rating modal (reuse from resource_detail.js)
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

// Initialize edit deck form
function initEditDeckForm() {
    const editForm = document.getElementById('editDeckForm');
    if (!editForm) return;
    
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const deckId = this.dataset.deckId;
        const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
        const submitBtn = this.querySelector('button[type="submit"]');
        
        const formData = new FormData();
        formData.append('title', document.getElementById('editDeckTitle').value);
        formData.append('description', document.getElementById('editDeckDescription').value);
        formData.append('category', document.getElementById('editDeckCategory').value);
        formData.append('visibility', document.getElementById('editDeckVisibility').checked ? 'public' : 'private');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        fetch(`/flashcards/deck/${deckId}/edit/`, {
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
                const modal = bootstrap.Modal.getInstance(document.getElementById('editDeckModal'));
                modal.hide();
                
                // Show success message
                alert('Deck updated successfully!');
                
                // Reload page if visibility changed
                if (data.visibility_changed) {
                    location.reload();
                }
            } else {
                alert(data.message || 'Error updating deck');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save Changes';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating deck');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Changes';
        });
    });
}
