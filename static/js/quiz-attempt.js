/**
 * Quiz Attempt Functionality
 * Handles form submission and validation for quiz attempts
 */

document.addEventListener('DOMContentLoaded', function() {
  const quizForm = document.getElementById('quiz-form');

  if (quizForm) {
    quizForm.addEventListener('submit', function(e) {
      e.preventDefault();

      // Get the selected answer
      const selectedAnswer = document.querySelector('input[name="answer"]:checked');
      
      if (!selectedAnswer) {
        console.log('No answer selected');
        return;
      }

      // Submit the form
      this.submit();
    });
  }

  // Optional: Add keyboard navigation
  addKeyboardNavigation();
});

/**
 * Keyboard Navigation
 * - Arrow keys to navigate between options
 * - Enter to submit answer
 */
function addKeyboardNavigation() {
  const optionInputs = document.querySelectorAll('.quiz-attempt__option-input');

  if (optionInputs.length === 0) return;

  document.addEventListener('keydown', function(e) {
    const currentIndex = Array.from(optionInputs).findIndex(
      (input) => input.checked
    );

    let nextIndex = currentIndex;

    // Arrow down or right: next option
    if ((e.key === 'ArrowDown' || e.key === 'ArrowRight') && currentIndex < optionInputs.length - 1) {
      nextIndex = currentIndex + 1;
      e.preventDefault();
    }

    // Arrow up or left: previous option
    if ((e.key === 'ArrowUp' || e.key === 'ArrowLeft') && currentIndex > 0) {
      nextIndex = currentIndex - 1;
      e.preventDefault();
    }

    // Update selection if changed
    if (nextIndex !== currentIndex) {
      optionInputs[nextIndex].checked = true;
    }

    // Enter key: submit form
    if (e.key === 'Enter' && document.querySelector('input[name="answer"]:checked')) {
      document.getElementById('quiz-form').submit();
    }
  });
}
