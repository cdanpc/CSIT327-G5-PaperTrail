from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Quiz, Question, Option, QuizAttempt, QuizAttemptAnswer
from .forms import QuizForm, QuestionForm, QuizAttemptForm
import json


@login_required
def quiz_list(request):
    """List all verified quizzes"""
    quizzes = Quiz.objects.filter(verification_status='verified').order_by('-created_at')
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'quizzes/quiz_list.html', context)


@login_required
def quiz_create(request):
    """Create a new quiz"""
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.creator = request.user
            
            # Auto-approve quizzes from professors
            if request.user.is_professor:
                quiz.verification_status = 'verified'
                quiz.verification_by = request.user
                quiz.verified_at = timezone.now()
            
            quiz.save()
            
            # Parse questions from JSON
            try:
                questions_data = json.loads(request.POST.get('questions_data', '[]'))
                
                for idx, q_data in enumerate(questions_data):
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=q_data['question_text'],
                        question_type=q_data['question_type'],
                        correct_answer=q_data['correct_answer'],
                        order=idx
                    )
                    
                    # Create options for multiple choice
                    if q_data['question_type'] == 'multiple_choice':
                        options = [
                            q_data.get('option_1', ''),
                            q_data.get('option_2', ''),
                            q_data.get('option_3', ''),
                            q_data.get('option_4', ''),
                        ]
                        for opt_idx, opt_text in enumerate(options):
                            if opt_text.strip():  # Only create non-empty options
                                Option.objects.create(
                                    question=question,
                                    option_text=opt_text,
                                    order=opt_idx
                                )
                
                if request.user.is_professor:
                    messages.success(request, 'Quiz created and published successfully!')
                else:
                    messages.success(request, 'Quiz created successfully! It is pending verification.')
                
                return redirect('quizzes:quiz_detail', pk=quiz.pk)
            except json.JSONDecodeError:
                messages.error(request, 'Error processing questions. Please try again.')
        
        messages.error(request, 'Please correct the errors below.')
    else:
        quiz_form = QuizForm()
    
    context = {
        'form': quiz_form,
    }
    return render(request, 'quizzes/quiz_create.html', context)


@login_required
def quiz_detail(request, pk):
    """View quiz details"""
    quiz = get_object_or_404(Quiz, pk=pk)
    
    # Check if user has already attempted this quiz
    user_attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user)
    has_attempted = user_attempts.exists()
    best_attempt = user_attempts.order_by('-score').first() if has_attempted else None
    
    context = {
        'quiz': quiz,
        'has_attempted': has_attempted,
        'best_attempt': best_attempt,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
def quiz_attempt(request, pk):
    """Start or continue a quiz attempt"""
    quiz = get_object_or_404(Quiz, pk=pk)
    
    # Only verified quizzes can be attempted
    if quiz.verification_status != 'verified':
        messages.error(request, 'This quiz is not available yet.')
        return redirect('quizzes:quiz_list')
    
    # Get or create an attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        quiz=quiz,
        student=request.user,
        completed_at__isnull=True,
        defaults={'total_questions': quiz.total_questions}
    )
    
    if created:
        quiz.increment_attempts_count()
    
    # Get unanswered questions
    answered_question_ids = attempt.answers.values_list('question_id', flat=True)
    all_questions = quiz.questions.all()
    unanswered_questions = all_questions.exclude(id__in=answered_question_ids)
    
    # Get current question (first unanswered or first question)
    if unanswered_questions.exists():
        current_question = unanswered_questions.first()
    elif all_questions.exists():
        # All questions answered, go to results
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect('quizzes:quiz_results', attempt_pk=attempt.pk)
    else:
        messages.error(request, 'This quiz has no questions.')
        return redirect('quizzes:quiz_detail', pk=quiz.pk)
    
    # Get question number (using order field)
    question_number = current_question.order + 1 if current_question.order else 1
    
    # Calculate progress percentage
    progress_percentage = int((question_number / quiz.total_questions) * 100) if quiz.total_questions > 0 else 0
    
    if request.method == 'POST':
        form = QuizAttemptForm(current_question, request.POST)
        
        if form.is_valid():
            answer_text = form.cleaned_data['answer']
            
            # For multiple choice, convert option ID to option text
            if current_question.question_type == 'multiple_choice':
                try:
                    option = Option.objects.get(id=int(answer_text), question=current_question)
                    answer_text = option.option_text
                except (Option.DoesNotExist, ValueError):
                    messages.error(request, 'Invalid option selected.')
                    return redirect('quizzes:quiz_attempt', pk=quiz.pk)
            
            # Check if answer is correct (case-insensitive for fill in blank)
            is_correct = False
            if current_question.question_type == 'multiple_choice':
                # For multiple choice, compare the option text directly
                is_correct = answer_text.strip().lower() == current_question.correct_answer.strip().lower()
            else:
                # For fill in blank, compare case-insensitively
                is_correct = answer_text.strip().lower() == current_question.correct_answer.strip().lower()
            
            # Save answer
            QuizAttemptAnswer.objects.update_or_create(
                attempt=attempt,
                question=current_question,
                defaults={
                    'answer_text': answer_text,
                    'is_correct': is_correct
                }
            )
            
            # Update score if correct
            if is_correct:
                attempt.score += 1
                attempt.save(update_fields=['score'])
            
            # Check if this was the last question
            remaining = unanswered_questions.exclude(id=current_question.id)
            if not remaining.exists():
                # Quiz completed
                attempt.completed_at = timezone.now()
                attempt.save()
                return redirect('quizzes:quiz_results', attempt_pk=attempt.pk)
            
            # Redirect to next question
            return redirect('quizzes:quiz_attempt', pk=quiz.pk)
    else:
        form = QuizAttemptForm(current_question)
    
    context = {
        'quiz': quiz,
        'question': current_question,
        'question_number': question_number,
        'total_questions': quiz.total_questions,
        'progress_percentage': progress_percentage,
        'form': form,
        'attempt': attempt,
    }
    return render(request, 'quizzes/quiz_attempt.html', context)


@login_required
def quiz_results(request, attempt_pk):
    """Show quiz attempt results"""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, student=request.user)
    
    # Ensure attempt is completed
    if not attempt.completed_at:
        attempt.completed_at = timezone.now()
        attempt.save()
    
    # Get all answers
    answers = attempt.answers.select_related('question').all()
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'answers': answers,
        'percentage': attempt.percentage,
    }
    return render(request, 'quizzes/quiz_results.html', context)


@login_required
def quiz_history(request):
    """Show user's quiz attempt history"""
    attempts = QuizAttempt.objects.filter(
        student=request.user,
        completed_at__isnull=False
    ).select_related('quiz').order_by('-completed_at')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'quizzes/quiz_history.html', context)


@login_required
def quiz_moderation_list(request):
    """List quizzes pending verification (professors only)"""
    if not request.user.is_professor:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('quizzes:quiz_list')
    
    pending_quizzes = Quiz.objects.filter(
        verification_status='pending'
    ).order_by('-created_at')
    
    context = {
        'pending_quizzes': pending_quizzes,
    }
    return render(request, 'quizzes/moderation_list.html', context)


@login_required
@require_http_methods(["POST"])
def approve_quiz(request, pk):
    """Approve a quiz (professors only)"""
    if not request.user.is_professor:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.verification_status = 'verified'
    quiz.verification_by = request.user
    quiz.verified_at = timezone.now()
    quiz.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    
    messages.success(request, f'"{quiz.title}" approved and published.')
    return redirect('quizzes:quiz_moderation_list')


@login_required
@require_http_methods(["POST"])
def reject_quiz(request, pk):
    """Reject a quiz (professors only)"""
    if not request.user.is_professor:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.verification_status = 'not_verified'
    quiz.verification_by = request.user
    quiz.verified_at = timezone.now()
    quiz.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    
    messages.info(request, f'"{quiz.title}" has been rejected.')
    return redirect('quizzes:quiz_moderation_list')

