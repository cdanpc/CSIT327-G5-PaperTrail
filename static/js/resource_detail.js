/**
 * Resource Detail Page - AJAX Handlers for Ratings and Comments
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // Get CSRF token from cookie
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

  // === SCROLL-AWARE STICKY COMMENT BAR ===
  (function initStickyCommentBar() {
    const stickyBar = document.getElementById('sticky-comment-bar-wrapper');
    if (!stickyBar) return;

    let lastScrollTop = 0;
    const checkScrollPosition = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Check if user scrolled to bottom (within 50px threshold)
      const isAtBottom = (scrollTop + windowHeight) >= (documentHeight - 50);
      
      if (isAtBottom) {
        // At bottom: unfix and let it sit at content end
        stickyBar.classList.remove('is-fixed');
        stickyBar.classList.add('is-unfixed');
      } else {
        // Not at bottom: fix to viewport bottom
        stickyBar.classList.add('is-fixed');
        stickyBar.classList.remove('is-unfixed');
      }
      
      lastScrollTop = scrollTop;
    };

    // Check on scroll with throttling
    let ticking = false;
    window.addEventListener('scroll', function() {
      if (!ticking) {
        window.requestAnimationFrame(function() {
          checkScrollPosition();
          ticking = false;
        });
        ticking = true;
      }
    });

    // Check on page load
    checkScrollPosition();

    // Check on window resize
    window.addEventListener('resize', checkScrollPosition);
  })();

  // === TEXTAREA AUTO-RESIZE ===
  (function initTextareaResize() {
    const textarea = document.getElementById('commentText');
    if (!textarea) return;

    function autoResize() {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    textarea.addEventListener('input', autoResize);
    textarea.addEventListener('focus', autoResize);
    
    // Reset on form submit
    const form = document.getElementById('commentForm');
    if (form) {
      form.addEventListener('submit', function() {
        setTimeout(() => {
          textarea.style.height = '48px';
        }, 100);
      });
    }
  })();

  // === HELPER FUNCTIONS ===
  
  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Show alert message (reusing existing alert system if available)
  function showAlert(message, type = 'info') {
    // Try to use existing toast/alert system
    if (typeof showToast === 'function') {
      showToast(message, type);
      return;
    }
    
    // Fallback: create a simple alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alertDiv.parentElement) {
        alertDiv.classList.remove('show');
        setTimeout(() => {
          if (alertDiv.parentElement) {
            alertDiv.remove();
          }
        }, 150);
      }
    }, 5000);
  }

  // === BOOKMARK TOGGLE (existing functionality) ===
  const bookmarkBtn = document.querySelector('.bookmark-toggle');
  if (bookmarkBtn) {
    bookmarkBtn.addEventListener('click', function () {
      const resourceId = this.getAttribute('data-resource-id');
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = `/bookmarks/toggle/${resourceId}/`;

      // CSRF token
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrftoken;
      form.appendChild(csrfInput);

      // Next redirect back to current page
      const nextInput = document.createElement('input');
      nextInput.type = 'hidden';
      nextInput.name = 'next';
      nextInput.value = window.location.pathname;
      form.appendChild(nextInput);

      document.body.appendChild(form);
      form.submit();
    });
  }

  // === LIKE BUTTON TOGGLE ===
  const likeButton = document.getElementById('likeButton');
  const likesStatValue = document.getElementById('likesStatValue');

  if (likeButton) {
    likeButton.addEventListener('click', async function() {
      const resourceId = this.closest('[data-resource-id]')?.getAttribute('data-resource-id') || 
                         window.location.pathname.match(/\/resources\/(\d+)\//)?.[1];

      if (!resourceId) {
        console.error('Resource ID not found');
        return;
      }

      // Disable during request
      this.disabled = true;
      this.style.opacity = '0.6';

      try {
        const response = await fetch(`/resources/${resourceId}/like/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (data.success) {
          // Update like count in stats
          if (likesStatValue) {
            likesStatValue.textContent = data.like_count;
          }

          // Update button appearance
          const icon = this.querySelector('i');
          if (data.action === 'liked') {
            this.classList.add('btn--liked');
            if (icon) {
              icon.classList.remove('far');
              icon.classList.add('fas');
            }
          } else {
            this.classList.remove('btn--liked');
            if (icon) {
              icon.classList.remove('fas');
              icon.classList.add('far');
            }
          }
        } else {
          showAlert(data.error || 'Failed to update like. Please try again.', 'danger');
        }
      } catch (error) {
        console.error('Error toggling like:', error);
        showAlert('An error occurred. Please try again.', 'danger');
      } finally {
        this.disabled = false;
        this.style.opacity = '1';
      }
    });
  }

  // === PREVIEW MODAL ===
  const previewModal = document.getElementById('previewModal');
  if (previewModal) {
    previewModal.addEventListener('show.bs.modal', function() {
      const resourceId = this.dataset.resourceId;
      const fileType = this.dataset.fileType;
      loadPreview(resourceId, fileType);
    });
  }

  function loadPreview(resourceId, fileType) {
    const previewLoading = document.getElementById('previewLoading');
    const previewContent = document.getElementById('previewContent');
    const previewError = document.getElementById('previewError');
    const errorMessage = document.getElementById('errorMessage');
    
    // Reset display states
    if (previewLoading) previewLoading.style.display = 'block';
    if (previewContent) previewContent.style.display = 'none';
    if (previewError) previewError.style.display = 'none';
    
    // Fetch preview from backend
    fetch(`/resources/${resourceId}/preview/`)
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.error || 'Failed to load preview');
          });
        }
        return response.json();
      })
      .then(data => {
        if (previewLoading) previewLoading.style.display = 'none';
        
        if (data.type === 'image') {
          const imagePreview = document.getElementById('imagePreview');
          const previewImage = document.getElementById('previewImage');
          if (previewImage) previewImage.src = `data:${data.mime_type};base64,${data.content}`;
          if (imagePreview) imagePreview.style.display = 'block';
          if (previewContent) previewContent.style.display = 'block';
        } 
        else if (data.type === 'pdf') {
          const pdfPreview = document.getElementById('pdfPreview');
          const pdfFrame = document.getElementById('pdfFrame');
          if (pdfFrame) pdfFrame.src = `data:application/pdf;base64,${data.content}`;
          if (pdfPreview) pdfPreview.style.display = 'block';
          if (previewContent) previewContent.style.display = 'block';
        }
        else if (data.type === 'text') {
          const textPreview = document.getElementById('textPreview');
          const textContent = document.getElementById('textContent');
          if (textContent) textContent.textContent = data.content;
          if (textPreview) textPreview.style.display = 'block';
          if (previewContent) previewContent.style.display = 'block';
        }
      })
      .catch(error => {
        if (previewLoading) previewLoading.style.display = 'none';
        if (previewError) previewError.style.display = 'block';
        if (errorMessage) errorMessage.textContent = error.message || 'Could not load file preview. Please try downloading the file instead.';
      });
  }

  // === RATING MODAL (NEW STYLE) ===
  (function initRatingModal() {
    const stars = document.querySelectorAll('.rating-star');
    const submitBtn = document.getElementById('submitRating');
    const ratingMessage = document.getElementById('ratingMessage');
    const ratingModal = document.getElementById('ratingModal');
    let selectedRating = 0;

    if (!stars.length || !submitBtn) return;

    stars.forEach(star => {
      star.addEventListener('click', function() {
        selectedRating = parseInt(this.dataset.rating);
        updateStars(selectedRating);
        submitBtn.disabled = false;
      });

      star.addEventListener('mouseenter', function() {
        const hoverRating = parseInt(this.dataset.rating);
        updateStars(hoverRating);
      });
    });

    const ratingStars = document.getElementById('ratingStars');
    if (ratingStars) {
      ratingStars.addEventListener('mouseleave', function() {
        updateStars(selectedRating);
      });
    }

    function updateStars(rating) {
      stars.forEach((star, index) => {
        if (index < rating) {
          star.classList.add('active');
        } else {
          star.classList.remove('active');
        }
      });
    }

    submitBtn.addEventListener('click', function() {
      if (selectedRating === 0) return;

      const rateUrl = this.dataset.rateUrl;

      fetch(rateUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ rating: selectedRating })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          if (ratingMessage) {
            ratingMessage.className = 'alert alert-success mt-3';
            ratingMessage.textContent = 'Thank you for your rating!';
            ratingMessage.style.display = 'block';
          }
          
          // Update the rating display
          const ratingStatValue = document.querySelector('.stat-card:nth-child(2) .stat-value');
          if (ratingStatValue && data.new_average) {
            ratingStatValue.textContent = parseFloat(data.new_average).toFixed(1);
          }

          setTimeout(() => {
            if (ratingModal && bootstrap && bootstrap.Modal) {
              const modalInstance = bootstrap.Modal.getInstance(ratingModal);
              if (modalInstance) modalInstance.hide();
            }
            selectedRating = 0;
            updateStars(0);
            submitBtn.disabled = true;
            if (ratingMessage) ratingMessage.style.display = 'none';
          }, 1500);
        } else {
          if (ratingMessage) {
            ratingMessage.className = 'rating-message alert-danger';
            ratingMessage.textContent = data.error || data.message || 'Something went wrong. Please try again.';
            ratingMessage.style.display = 'block';
          }
        }
      })
      .catch(error => {
        console.error('Rating error:', error);
        if (ratingMessage) {
          ratingMessage.className = 'rating-message alert-danger';
          ratingMessage.textContent = 'Error submitting rating. Please try again.';
          ratingMessage.style.display = 'block';
        }
      });
    });

    // Reset modal on close
    if (ratingModal) {
      ratingModal.addEventListener('hidden.bs.modal', function() {
        selectedRating = 0;
        updateStars(0);
        submitBtn.disabled = true;
        if (ratingMessage) ratingMessage.style.display = 'none';
      });
    }
  })();

  // === RATING SYSTEM ===
  (function initRatingSystem() {
    const ratingComponent = document.getElementById('rating-component');
    if (!ratingComponent) return;

    const currentSavedRating = parseInt(ratingComponent.dataset.currentRating) || 0;
    const rateUrl = ratingComponent.dataset.rateUrl;
    
    let selectedRating = 0;
    const stars = ratingComponent.querySelectorAll('.rating-star');
    const submitBtn = document.getElementById('submitRatingBtn');
    const editBtn = document.getElementById('editRatingBtn');
    const ratingText = document.getElementById('userRatingText');
    const starsContainer = ratingComponent.querySelector('.rating-stars');

    // If user has already rated, lock the stars initially
    let isLocked = currentSavedRating > 0;

    function updateStars(value) {
        stars.forEach(star => {
            const starVal = parseInt(star.dataset.value);
            if (starVal <= value) {
                star.classList.remove('far');
                star.classList.add('fas');
            } else {
                star.classList.remove('fas');
                star.classList.add('far');
            }
        });
    }

    // Initialize
    updateStars(currentSavedRating);
    if (isLocked) {
        starsContainer.style.pointerEvents = 'none';
        starsContainer.style.opacity = '0.7';
    } else {
        starsContainer.style.pointerEvents = 'auto';
        starsContainer.style.opacity = '1';
    }

    // Event Listeners
    stars.forEach(star => {
        star.addEventListener('mouseover', function() {
            if (!isLocked) updateStars(this.dataset.value);
        });
        
        star.addEventListener('mouseout', function() {
            if (!isLocked) updateStars(selectedRating || currentSavedRating);
        });

        star.addEventListener('click', function() {
            if (isLocked) return;
            selectedRating = parseInt(this.dataset.value);
            updateStars(selectedRating);
            if (submitBtn) submitBtn.disabled = false;
            if (ratingText) ratingText.textContent = `Selected: ${selectedRating} stars`;
        });
    });

    // Edit Button Logic
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            isLocked = false;
            starsContainer.style.pointerEvents = 'auto';
            starsContainer.style.opacity = '1';
            this.classList.add('d-none'); // Hide edit button
            if (submitBtn) {
                submitBtn.classList.remove('d-none'); // Show submit button
                submitBtn.disabled = true; // Disable until new selection
            }
            if (ratingText) ratingText.textContent = 'Select new rating';
        });
    }

    if (submitBtn) {
      submitBtn.addEventListener('click', function() {
          if (!selectedRating) return;
          
          this.disabled = true;
          this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

          fetch(rateUrl, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'X-CSRFToken': csrftoken,
                  'X-Requested-With': 'XMLHttpRequest'
              },
              body: 'stars=' + selectedRating
          })
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => {
              if (data.success) {
                  if (ratingText) ratingText.textContent = `You rated: ${selectedRating} stars`;
                  location.reload(); 
              } else {
                  throw new Error(data.error || 'Error submitting rating');
              }
          })
          .catch(error => {
              console.error('Error:', error);
              this.disabled = false;
              this.textContent = 'Update Rating';
              alert(error.message || 'An error occurred. Please try again.');
          });
      });
    }
  })();

  // === COMMENT EDIT/DELETE FUNCTIONALITY ===
  (function initCommentActions() {
    // Edit button click
    document.addEventListener('click', function(e) {
      if (e.target.classList.contains('comment-edit-btn') || e.target.closest('.comment-edit-btn')) {
        e.preventDefault();
        const btn = e.target.classList.contains('comment-edit-btn') ? e.target : e.target.closest('.comment-edit-btn');
        const commentId = btn.dataset.commentId;
        const commentText = document.querySelector(`.comment-text[data-comment-id="${commentId}"]`);
        const editTextarea = document.querySelector(`.comment-edit-textarea[data-comment-id="${commentId}"]`);
        const saveBtn = document.querySelector(`.comment-save-btn[data-comment-id="${commentId}"]`);
        const cancelBtn = document.querySelector(`.comment-cancel-btn[data-comment-id="${commentId}"]`);
        const replyBtn = document.querySelector(`.reply-btn[data-comment-id="${commentId}"]`);
        
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
        fetch(`/resources/comment/${commentId}/edit/`, {
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
            // Update the comment text display - find the container and update the paragraph inside
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
    });
  })();
});
