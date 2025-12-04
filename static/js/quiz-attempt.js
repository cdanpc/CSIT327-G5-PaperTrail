/**
 * Quiz Attempt Functionality
 * Handles form submission and validation for quiz attempts
 */

document.addEventListener('DOMContentLoaded', function() {
  const quizForm = document.getElementById('quiz-form');

  if (quizForm) {
    quizForm.addEventListener('submit', function(e) {
      // For multiple choice, check if answer is selected
      const radioInputs = document.querySelectorAll('input[type="radio"][name="answer"]');
      if (radioInputs.length > 0) {
        const selectedAnswer = document.querySelector('input[name="answer"]:checked');
        if (!selectedAnswer) {
          e.preventDefault();
          alert('Please select an answer before proceeding.');
          return false;
        }
      }
      
      // For fill-in-the-blank, check if text is entered
      const textInput = document.querySelector('input[type="text"][name="answer"]');
      if (textInput && textInput.value.trim() === '') {
        e.preventDefault();
        alert('Please enter an answer before proceeding.');
        return false;
      }
      
      // Allow form submission
      return true;
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
