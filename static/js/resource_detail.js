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
});
