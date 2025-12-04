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

// === COMMENT FUNCTIONALITY (Copied from resource_detail.js) ===
(function() {
    // Get CSRF token
    function getCookie(name) {
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
    const csrftoken = getCookie('csrftoken');

    // === COMMENT EDIT/DELETE FUNCTIONALITY ===
    document.addEventListener('click', function(e) {
        // Edit button click
        if (e.target.classList.contains('comment-edit-btn') || e.target.closest('.comment-edit-btn')) {
            e.preventDefault();
            const btn = e.target.classList.contains('comment-edit-btn') ? e.target : e.target.closest('.comment-edit-btn');
            const commentId = btn.dataset.commentId;
            const commentText = document.querySelector(`.comment-text[data-comment-id="${commentId}"]`);
            const editTextarea = document.querySelector(`.comment-edit-textarea[data-comment-id="${commentId}"]`);
            const saveBtn = document.querySelector(`.comment-save-btn[data-comment-id="${commentId}"]`);
            const cancelBtn = document.querySelector(`.comment-cancel-btn[data-comment-id="${commentId}"]`);
            const replyBtn = document.querySelector(`.reply-btn-text[data-comment-id="${commentId}"]`);
            
            if (commentText && editTextarea && saveBtn && cancelBtn) {
                commentText.classList.add('d-none');
                editTextarea.classList.remove('d-none');
                saveBtn.classList.remove('d-none');
                cancelBtn.classList.remove('d-none');
                if (replyBtn) replyBtn.classList.add('d-none');
                editTextarea.focus();
            }
        }
        
        // Cancel button click
        if (e.target.classList.contains('comment-cancel-btn') || e.target.closest('.comment-cancel-btn')) {
            const btn = e.target.classList.contains('comment-cancel-btn') ? e.target : e.target.closest('.comment-cancel-btn');
            const commentId = btn.dataset.commentId;
            const commentText = document.querySelector(`.comment-text[data-comment-id="${commentId}"]`);
            const editTextarea = document.querySelector(`.comment-edit-textarea[data-comment-id="${commentId}"]`);
            const saveBtn = document.querySelector(`.comment-save-btn[data-comment-id="${commentId}"]`);
            const cancelBtn = document.querySelector(`.comment-cancel-btn[data-comment-id="${commentId}"]`);
            const replyBtn = document.querySelector(`.reply-btn-text[data-comment-id="${commentId}"]`);
            
            if (commentText && editTextarea && saveBtn && cancelBtn) {
                commentText.classList.remove('d-none');
                editTextarea.classList.add('d-none');
                saveBtn.classList.add('d-none');
                cancelBtn.classList.add('d-none');
                if (replyBtn) replyBtn.classList.remove('d-none');
                // Reset textarea to original value
                editTextarea.value = commentText.textContent.trim();
            }
        }
        
        // Save button click
        if (e.target.classList.contains('comment-save-btn') || e.target.closest('.comment-save-btn')) {
            const btn = e.target.classList.contains('comment-save-btn') ? e.target : e.target.closest('.comment-save-btn');
            const commentId = btn.dataset.commentId;
            const editTextarea = document.querySelector(`.comment-edit-textarea[data-comment-id="${commentId}"]`);
            const newText = editTextarea.value.trim();
            
            if (!newText) {
                alert('Comment cannot be empty');
                return;
            }
            
            // Disable button while saving
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            
            // Send AJAX request to update comment
            fetch(`/flashcards/comment/${commentId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: 'text=' + encodeURIComponent(newText)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the comment text display
                    const commentTextContainer = document.querySelector(`.comment-text[data-comment-id="${commentId}"]`);
                    const commentParagraph = commentTextContainer.querySelector('p');
                    if (commentParagraph) {
                        commentParagraph.textContent = newText;
                    }
                    
                    // Hide edit mode
                    const saveBtn = document.querySelector(`.comment-save-btn[data-comment-id="${commentId}"]`);
                    const cancelBtn = document.querySelector(`.comment-cancel-btn[data-comment-id="${commentId}"]`);
                    const replyBtn = document.querySelector(`.reply-btn-text[data-comment-id="${commentId}"]`);
                    
                    commentTextContainer.classList.remove('d-none');
                    editTextarea.classList.add('d-none');
                    saveBtn.classList.add('d-none');
                    cancelBtn.classList.add('d-none');
                    if (replyBtn) replyBtn.classList.remove('d-none');
                    
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-check"></i> Save';
                } else {
                    throw new Error(data.error || 'Failed to update comment');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'An error occurred. Please try again.');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check"></i> Save';
            });
        }
        
        // Delete button click
        if (e.target.classList.contains('comment-delete-btn') || e.target.closest('.comment-delete-btn')) {
            e.preventDefault();
            const btn = e.target.classList.contains('comment-delete-btn') ? e.target : e.target.closest('.comment-delete-btn');
            const commentId = btn.dataset.commentId;
            const deleteUrl = btn.dataset.deleteUrl;
            
            if (confirm('Are you sure you want to delete this comment?')) {
                fetch(deleteUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Remove the comment from DOM
                        const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
                        if (commentElement) {
                            commentElement.remove();
                        }
                        // Update comment count
                        const commentsHeading = document.querySelector('.comments-heading');
                        if (commentsHeading) {
                            const countMatch = commentsHeading.textContent.match(/\((\d+)\)/);
                            if (countMatch) {
                                const newCount = parseInt(countMatch[1]) - 1;
                                commentsHeading.textContent = `Comments (${newCount})`;
                            }
                        }
                    } else {
                        throw new Error('Failed to delete comment');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                });
            }
        }

        // === REPLY FUNCTIONALITY ===
        // Reply button click
        if (e.target.classList.contains('reply-btn-text') || e.target.closest('.reply-btn-text')) {
            e.preventDefault();
            const btn = e.target.classList.contains('reply-btn-text') ? e.target : e.target.closest('.reply-btn-text');
            const commentId = btn.dataset.commentId;
            const replyFormContainer = document.querySelector(`.reply-form-container[data-comment-id="${commentId}"]`);
            
            if (replyFormContainer) {
                replyFormContainer.classList.remove('d-none');
                // Focus textarea
                const textarea = replyFormContainer.querySelector('textarea');
                if (textarea) textarea.focus();
                // Hide reply button
                btn.classList.add('d-none');
            }
        }
        
        // Reply Cancel button click
        if (e.target.classList.contains('reply-cancel-btn') || e.target.closest('.reply-cancel-btn')) {
            e.preventDefault();
            const btn = e.target.classList.contains('reply-cancel-btn') ? e.target : e.target.closest('.reply-cancel-btn');
            const commentId = btn.dataset.commentId;
            const replyFormContainer = document.querySelector(`.reply-form-container[data-comment-id="${commentId}"]`);
            const replyBtn = document.querySelector(`.reply-btn-text[data-comment-id="${commentId}"]`);
            
            if (replyFormContainer) {
                replyFormContainer.classList.add('d-none');
                // Show reply button again
                if (replyBtn) replyBtn.classList.remove('d-none');
            }
        }
    });
})();
