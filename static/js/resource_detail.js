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

  // === LIKE BUTTON TOGGLE (NEW) ===
  const likeIcon = document.getElementById('likeIcon');
  const likeCount = document.getElementById('likeCount');

  if (likeIcon) {
    likeIcon.addEventListener('click', async function() {
      const resourceId = this.getAttribute('data-resource-id');

      // Disable during request
      this.style.pointerEvents = 'none';
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
          // Update like count
          likeCount.textContent = data.like_count;

          // Update icon appearance with new classes
          if (data.action === 'liked') {
            this.classList.remove('unliked');
            this.classList.add('liked');
            this.setAttribute('title', 'Unlike');
          } else {
            this.classList.remove('liked');
            this.classList.add('unliked');
            this.setAttribute('title', 'Like');
          }
        } else {
          showAlert(data.error || 'Failed to update like. Please try again.', 'danger');
        }
      } catch (error) {
        console.error('Error toggling like:', error);
        showAlert('An error occurred. Please try again.', 'danger');
      } finally {
        this.style.pointerEvents = 'auto';
        this.style.opacity = '1';
      }
    });
  }

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
});
