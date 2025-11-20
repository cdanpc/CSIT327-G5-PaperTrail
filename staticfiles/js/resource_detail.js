document.addEventListener('DOMContentLoaded', function() {
  // Star rating interaction
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

  // Bookmark toggle
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
      const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
      if (csrfCookie) {
        csrfInput.value = csrfCookie.split('=')[1];
      }
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
