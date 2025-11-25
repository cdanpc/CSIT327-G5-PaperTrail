// Quizzes module scripts
// Handles dynamic quiz creation (add/remove questions, validation, payload build)


(function () {
  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  function applyDataWidth() {
    // Set width for progress bars using data-width to avoid inline CSS with template braces
    document.querySelectorAll('.progress-bar[data-width]')
      .forEach(function (el) {
        var val = el.getAttribute('data-width');
        if (val !== null && val !== '') {
          el.style.width = String(val).trim() + '%';
        }
      });
  }

  ready(function () {
    // Always apply data-widths on any quizzes page
    applyDataWidth();

    const addBtn = document.getElementById('addQuestionBtn');
    const form = document.getElementById('quizCreateForm');

    if (!form || !addBtn) {
      // Not on the quiz create page; nothing more to do
      return;
    }

    let questionCount = 0;

    addBtn.addEventListener('click', function () {
      addQuestion();
    });

    function addQuestion() {
      questionCount++;
      const questionsContainer = document.getElementById('questionsContainer');
      const noQuestions = document.getElementById('noQuestions');
      if (noQuestions) noQuestions.style.display = 'none';

      const questionDiv = document.createElement('div');
      questionDiv.className = 'question-item mb-4';
      questionDiv.id = `question-${questionCount}`;
      questionDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="mb-0"><i class="fas fa-question"></i> Question ${questionCount}</h6>
          <button type="button" class="btn btn-sm btn-outline-danger" data-remove-question="${questionCount}">
            <i class="fas fa-trash"></i> Remove
          </button>
        </div>
        <div class="mb-3">
          <label class="form-label">Question Text <span class="text-danger">*</span></label>
          <textarea class="form-control question-text" rows="3" placeholder="Enter your question here..." required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Question Type <span class="text-danger">*</span></label>
          <select class="form-select question-type" data-question-id="${questionCount}" required>
            <option value="">Select type</option>
            <option value="multiple_choice">Multiple Choice</option>
            <option value="fill_in_blank">Fill in the Blank</option>
          </select>
        </div>
        <div class="multiple-choice-options" style="display: none;">
          <label class="form-label">Options <span class="text-danger">*</span></label>
          <div class="row g-2 mb-2">
            <div class="col-md-6">
              <input type="text" class="form-control option-input" placeholder="Option 1" data-option="1">
            </div>
            <div class="col-md-6">
              <input type="text" class="form-control option-input" placeholder="Option 2" data-option="2">
            </div>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-md-6">
              <input type="text" class="form-control option-input" placeholder="Option 3" data-option="3">
            </div>
            <div class="col-md-6">
              <input type="text" class="form-control option-input" placeholder="Option 4" data-option="4">
            </div>
          </div>
          <label class="form-label">Select Correct Answer <span class="text-danger">*</span></label>
          <div class="row g-2 mb-2">
            <div class="col-md-3">
              <input type="radio" class="btn-check correct-answer-radio" id="radio-correct-${questionCount}-1" name="correct-answer-radio-${questionCount}" data-option="1">
              <label class="btn btn-outline-success w-100" for="radio-correct-${questionCount}-1" style="cursor: pointer;">Option 1</label>
            </div>
            <div class="col-md-3">
              <input type="radio" class="btn-check correct-answer-radio" id="radio-correct-${questionCount}-2" name="correct-answer-radio-${questionCount}" data-option="2">
              <label class="btn btn-outline-success w-100" for="radio-correct-${questionCount}-2" style="cursor: pointer;">Option 2</label>
            </div>
            <div class="col-md-3">
              <input type="radio" class="btn-check correct-answer-radio" id="radio-correct-${questionCount}-3" name="correct-answer-radio-${questionCount}" data-option="3">
              <label class="btn btn-outline-success w-100" for="radio-correct-${questionCount}-3" style="cursor: pointer;">Option 3</label>
            </div>
            <div class="col-md-3">
              <input type="radio" class="btn-check correct-answer-radio" id="radio-correct-${questionCount}-4" name="correct-answer-radio-${questionCount}" data-option="4">
              <label class="btn btn-outline-success w-100" for="radio-correct-${questionCount}-4" style="cursor: pointer;">Option 4</label>
            </div>
          </div>
          <input type="hidden" class="selected-correct-option" value="">
        </div>
        <div class="mb-3" style="display: none;">
          <label class="form-label">Correct Answer <span class="text-danger">*</span></label>
          <input type="text" class="form-control correct-answer correct-answer-text" placeholder="Enter correct answer" required>
          <small class="text-muted correct-answer-hint">For fill in blank: enter the answer.</small>
        </div>
      `;

      questionsContainer.appendChild(questionDiv);
    }

    document.addEventListener('click', function (e) {
      const removeBtn = e.target.closest('[data-remove-question]');
      if (removeBtn) {
        const id = removeBtn.getAttribute('data-remove-question');
        removeQuestion(id);
      }
    });

    function removeQuestion(id) {
      const questionDiv = document.getElementById(`question-${id}`);
      if (questionDiv) questionDiv.remove();
      updateQuestionNumbers();
      if (document.getElementById('questionsContainer').children.length === 0) {
        const noQuestions = document.getElementById('noQuestions');
        if (noQuestions) noQuestions.style.display = 'block';
      }
    }

    document.addEventListener('change', function (e) {
      if (e.target && e.target.classList.contains('question-type')) {
        const select = e.target;
        const questionId = select.getAttribute('data-question-id');
        toggleQuestionType(questionId);
      } else if (e.target && e.target.classList.contains('option-input')) {
        // Update when options change
        const questionDiv = e.target.closest('.question-item');
        if (questionDiv) {
          const questionType = questionDiv.querySelector('.question-type').value;
          if (questionType === 'multiple_choice') {
            updateOptionLabels(questionDiv);
          }
        }
      } else if (e.target && e.target.classList.contains('correct-answer-radio')) {
        // Handle correct answer radio button selection
        const questionDiv = e.target.closest('.question-item');
        const selectedOption = e.target.getAttribute('data-option');
        const optionInput = questionDiv.querySelector(`.option-input[data-option="${selectedOption}"]`);
        const hiddenInput = questionDiv.querySelector('.selected-correct-option');
        hiddenInput.value = optionInput.value.trim();
      }
    });

    function updateOptionLabels(questionDiv) {
      // Update the button labels to show actual option text
      const buttons = questionDiv.querySelectorAll('label[for^="radio-correct-"]');
      const optionInputs = questionDiv.querySelectorAll('.option-input');
      
      buttons.forEach((btn, index) => {
        const optionText = optionInputs[index]?.value.trim() || `Option ${index + 1}`;
        btn.textContent = optionText || `Option ${index + 1}`;
      });
    }

    function toggleQuestionType(questionId) {
      const questionDiv = document.getElementById(`question-${questionId}`);
      if (!questionDiv) return;
      const questionType = questionDiv.querySelector('.question-type').value;
      const optionsDiv = questionDiv.querySelector('.multiple-choice-options');
      const correctAnswerDiv = optionsDiv.nextElementSibling;
      const correctAnswerText = questionDiv.querySelector('.correct-answer-text');
      const correctAnswerHint = questionDiv.querySelector('.correct-answer-hint');

      if (questionType === 'multiple_choice') {
        optionsDiv.style.display = 'block';
        correctAnswerDiv.style.display = 'none';
        correctAnswerText.removeAttribute('required');
        correctAnswerHint.textContent = 'Select the correct answer by clicking one of the option buttons above.';
        updateOptionLabels(questionDiv);
      } else if (questionType === 'fill_in_blank') {
        optionsDiv.style.display = 'none';
        correctAnswerDiv.style.display = 'block';
        correctAnswerText.setAttribute('required', '');
        correctAnswerText.placeholder = 'Enter correct answer';
        correctAnswerHint.textContent = 'For fill in blank: enter the answer.';
      }
    }

    function updateQuestionNumbers() {
      const questions = document.querySelectorAll('.question-item');
      questions.forEach((q, index) => {
        const title = q.querySelector('h6');
        if (title) title.innerHTML = `<i class="fas fa-question"></i> Question ${index + 1}`;
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const questions = [];
      const questionItems = document.querySelectorAll('.question-item');

      if (questionItems.length === 0) {
        alert('Please add at least one question.');
        return;
      }

      let isValid = true;
      questionItems.forEach((item, index) => {
        const questionText = item.querySelector('.question-text')?.value.trim();
        const questionType = item.querySelector('.question-type')?.value;
        
        // Get correct answer based on question type
        let correctAnswer = '';
        if (questionType === 'multiple_choice') {
          correctAnswer = item.querySelector('.selected-correct-option')?.value.trim();
          if (!correctAnswer) {
            isValid = false;
            alert(`Question ${index + 1}: Please select the correct answer by clicking "Correct" on one of the options.`);
            return;
          }
        } else {
          correctAnswer = item.querySelector('.correct-answer-text')?.value.trim();
        }

        if (!questionText || !questionType || !correctAnswer) {
          isValid = false;
          return;
        }

        const questionData = {
          question_text: questionText,
          question_type: questionType,
          correct_answer: correctAnswer,
        };

        if (questionType === 'multiple_choice') {
          const options = [];
          item.querySelectorAll('.option-input').forEach((input) => {
            const val = input.value.trim();
            if (val) options.push(val);
          });

          if (options.length < 2) {
            isValid = false;
            alert(`Question ${index + 1}: Multiple choice questions need at least 2 options.`);
            return;
          }

          questionData.option_1 = options[0] || '';
          questionData.option_2 = options[1] || '';
          questionData.option_3 = options[2] || '';
          questionData.option_4 = options[3] || '';
        }

        questions.push(questionData);
      });

      if (!isValid) {
        alert('Please fill in all required fields for all questions.');
        return;
      }

      const input = document.getElementById('questionsDataInput');
      input.value = JSON.stringify(questions);
      form.submit();
    });
  });
})();
