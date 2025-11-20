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

  // === RATING SUBMISSION (AJAX) ===
  const ratingForm = document.querySelector('form[action*="/rate/"]');
  
  if (ratingForm) {
    ratingForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(ratingForm);
      const submitBtn = ratingForm.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn.innerHTML;
      
      // Validate that a rating is selected
      const starsValue = formData.get('stars');
      if (!starsValue) {
        showAlert('Please select a star rating before submitting.', 'warning');
        return;
      }
      
      // Disable button during submission
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
      
      try {
        const response = await fetch(ratingForm.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
          },
          body: formData,
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Update the UI with new rating data
          updateRatingDisplay(data);
          
          // Show success message
          showAlert(data.message, 'success');
          
          // Update button text if it's now an update
          if (!data.created) {
            const btnIcon = submitBtn.querySelector('i') ? '<i class="fas fa-sync"></i> ' : '';
            submitBtn.innerHTML = btnIcon + 'Update';
          }
        } else {
          showAlert(data.error || 'Failed to submit rating. Please try again.', 'danger');
        }
      } catch (error) {
        console.error('Error submitting rating:', error);
        showAlert('An error occurred. Please try again.', 'danger');
      } finally {
        // Re-enable button
        submitBtn.disabled = false;
        if (submitBtn.innerHTML.includes('Submitting')) {
          submitBtn.innerHTML = originalBtnText;
        }
      }
    });
  }

  // Update rating display in the UI
  function updateRatingDisplay(data) {
    // Update average rating if displayed
    const avgRatingElem = document.querySelector('.average-rating, [data-avg-rating]');
    if (avgRatingElem && data.avg_rating !== undefined) {
      avgRatingElem.textContent = data.avg_rating.toFixed(1);
    }
    
    // Update rating count if displayed
    const ratingCountElem = document.querySelector('.rating-count, [data-rating-count]');
    if (ratingCountElem && data.rating_count !== undefined) {
      const pluralText = data.rating_count === 1 ? 'rating' : 'ratings';
      ratingCountElem.textContent = `${data.rating_count} ${pluralText}`;
    }
    
    // Update the current rating text under the form
    const currentRatingText = ratingForm.querySelector('small.text-muted');
    if (currentRatingText && data.user_stars) {
      const pluralStars = data.user_stars === 1 ? 'star' : 'stars';
      currentRatingText.textContent = `Your current rating: ${data.user_stars} ${pluralStars}`;
    } else if (!currentRatingText && data.user_stars && ratingForm) {
      // Create the rating text if it doesn't exist
      const small = document.createElement('small');
      small.className = 'text-muted';
      const pluralStars = data.user_stars === 1 ? 'star' : 'stars';
      small.textContent = `Your current rating: ${data.user_stars} ${pluralStars}`;
      ratingForm.appendChild(small);
    }
    
    // Update the select to show current rating
    const starsSelect = ratingForm.querySelector('select[name="stars"]');
    if (starsSelect && data.user_stars) {
      starsSelect.value = data.user_stars;
    }
  }

  // === COMMENT SUBMISSION (AJAX) ===
  const commentForm = document.querySelector('form[action*="/comment/"]');
  const commentsContainer = document.querySelector('#feedback-section .mt-3');
  
  if (commentForm) {
    commentForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(commentForm);
      const submitBtn = commentForm.querySelector('button[type="submit"]');
      const textarea = commentForm.querySelector('textarea[name="text"]');
      const originalBtnText = submitBtn.innerHTML;
      
      // Validate comment text
      const commentText = formData.get('text').trim();
      if (!commentText) {
        showAlert('Please enter a comment before submitting.', 'warning');
        return;
      }
      
      // Disable button and textarea during submission
      submitBtn.disabled = true;
      textarea.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
      
      try {
        const response = await fetch(commentForm.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
          },
          body: formData,
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Add the new comment to the DOM
          addCommentToDOM(data.comment);
          
          // Clear the textarea
          textarea.value = '';
          
          // Show success message
          showAlert(data.message, 'success');
          
          // Update "No comments yet" message if present
          const noCommentsMsg = commentsContainer?.querySelector('p.text-muted');
          if (noCommentsMsg && noCommentsMsg.textContent.includes('No comments yet')) {
            noCommentsMsg.remove();
          }
        } else {
          showAlert(data.error || 'Failed to post comment. Please try again.', 'danger');
        }
      } catch (error) {
        console.error('Error posting comment:', error);
        showAlert('An error occurred. Please try again.', 'danger');
      } finally {
        // Re-enable button and textarea
        submitBtn.disabled = false;
        textarea.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  // Add new comment to the DOM
  function addCommentToDOM(comment) {
    if (!commentsContainer) return;
    
    // Find or create the comments list container
    let commentsList = commentsContainer.querySelector('.comment-item')?.parentElement;
    
    // If no comments container exists, look for "No comments yet" message
    const noCommentsMsg = commentsContainer.querySelector('p.text-muted');
    if (noCommentsMsg && noCommentsMsg.textContent.includes('No comments yet')) {
      // Replace the "no comments" message with a new container
      const newContainer = document.createElement('div');
      newContainer.className = 'comments-list';
      noCommentsMsg.parentElement.replaceChild(newContainer, noCommentsMsg);
      commentsList = newContainer;
    }
    
    // If still no container, create one
    if (!commentsList) {
      commentsList = document.createElement('div');
      commentsList.className = 'comments-list';
      commentsContainer.appendChild(commentsList);
    }
    
    // Create comment HTML
    const commentHTML = `
      <div class="border-bottom pb-3 mb-3 comment-item">
        <div class="d-flex justify-content-between align-items-start">
          <div class="d-flex gap-3 flex-grow-1">
            <div class="avatar-circle avatar-40"><span class="text-white small fw-bold">${comment.user_initial}</span></div>
            <div class="flex-grow-1">
              <div class="d-flex align-items-center gap-2 mb-1">
                <strong class="title-strong">${escapeHtml(comment.user_name)}</strong>
                ${comment.is_professor ? '<span class="badge badge-professor badge-sm">Professor</span>' : ''}
              </div>
              <small class="text-muted d-block mb-2">${comment.created_at}</small>
              <p class="mb-0 para-muted lh-16">${escapeHtml(comment.text).replace(/\n/g, '<br>')}</p>
            </div>
          </div>
          ${comment.can_delete ? `
            <button type="button" class="btn btn-sm btn-outline-danger" title="Delete" 
                    onclick="if(confirm('Are you sure you want to delete this comment?')) { location.href='${comment.delete_url}'; }">
              <i class="fas fa-trash"></i>
            </button>
          ` : ''}
        </div>
      </div>
    `;
    
    // Insert the new comment at the beginning of the comments list
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = commentHTML;
    const newComment = tempDiv.firstElementChild;
    
    // Insert before the first comment or at the end if no comments
    const firstComment = commentsList.querySelector('.comment-item');
    if (firstComment) {
      commentsList.insertBefore(newComment, firstComment);
    } else {
      commentsList.appendChild(newComment);
    }
  }

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

  // === EXISTING STAR RATING INTERACTION (for visual feedback) ===
  const starLabels = document.querySelectorAll('.star-label');
  const starIcons = document.querySelectorAll('.star-icon');

  starLabels.forEach((label) => {
    label.addEventListener('click', function() {
      const input = this.querySelector('input[type="radio"]');
      const value = parseInt(input.value, 10);

      starIcons.forEach((icon, i) => {
        if (i < value) {
          icon.classList.remove('far');
          icon.classList.add('fas');
        } else {
          icon.classList.remove('fas');
          icon.classList.add('far');
        }
      });
    });

    label.addEventListener('mouseenter', function() {
      const value = parseInt(this.querySelector('input[type="radio"]').value, 10);
      starIcons.forEach((icon, i) => {
        if (i < value) {
          icon.style.opacity = '1';
          icon.classList.add('fas');
          icon.classList.remove('far');
        }
      });
    });
  });

  const starContainer = document.querySelector('.star-rating-container');
  if (starContainer) {
    starContainer.addEventListener('mouseleave', function() {
      const checkedInput = document.querySelector('input[name="stars"]:checked');
      if (checkedInput) {
        const value = parseInt(checkedInput.value, 10);
        starIcons.forEach((icon, i) => {
          if (i < value) {
            icon.classList.remove('far');
            icon.classList.add('fas');
          } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
          }
        });
      } else {
        starIcons.forEach(icon => {
          icon.classList.remove('fas');
          icon.classList.add('far');
        });
      }
    });
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
});
