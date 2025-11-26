from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Quiz, Question, Option, QuizAttempt, QuizAttemptAnswer, QuizBookmark
from .forms import QuizForm, QuestionForm, QuizAttemptForm
from django.core.mail import send_mail
import json


@login_required
def quiz_list(request):
    """List quizzes with All/My scopes and optional search.

    - All: verified AND public quizzes (plus pending for professors)
    - My: quizzes created by current user (any verification, any visibility)
    - Search: filter by title or description substring (case-insensitive)
    """
    scope = request.GET.get('scope', 'all')
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    if scope == 'mine':
        quizzes = Quiz.objects.filter(creator=request.user).order_by('-created_at')
    else:
        if getattr(request.user, 'is_professor', False):
            quizzes = Quiz.objects.filter(is_public=True).filter(
                Q(verification_status='verified') | Q(verification_status='pending')
            ).order_by('-created_at')
        else:
            quizzes = Quiz.objects.filter(verification_status='verified', is_public=True).order_by('-created_at')
    
    if q:
        quizzes = quizzes.filter(Q(title__icontains=q) | Q(description__icontains=q))
    
    if status_filter:
        quizzes = quizzes.filter(verification_status=status_filter)
    # Bookmarks for current user
    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(
            QuizBookmark.objects.filter(user=request.user, quiz__in=quizzes).values_list('quiz_id', flat=True)
        )
    
    # Add like status for each quiz
    for quiz in quizzes:
        if request.user.is_authenticated:
            quiz.user_has_liked = quiz.likes.filter(user=request.user).exists()
        else:
            quiz.user_has_liked = False

    # Status filter options for component
    status_filter_options = [
        {'value': '', 'label': 'All Status'},
        {'value': 'verified', 'label': 'Verified'},
        {'value': 'pending', 'label': 'Pending'},
        {'value': 'rejected', 'label': 'Rejected'},
    ]

    context = {
        'quizzes': quizzes,
        'scope': scope,
        'query': q,
        'bookmarked_ids': bookmarked_ids,
        'scope_html': f'<input type="hidden" name="scope" value="{scope}">' if scope else '',
        'status_filter': status_filter,
        'status_filter_options': status_filter_options,
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
            # Verification workflow
            if request.user.is_professor:
                # Professors: auto-verify regardless of visibility
                quiz.verification_status = 'verified'
                quiz.verification_by = request.user
                quiz.verified_at = timezone.now()
            else:
                # Students: public -> pending, private -> verified
                if quiz.is_public:
                    quiz.verification_status = 'pending'
                    quiz.verification_by = None
                    quiz.verified_at = None
                else:
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
def quiz_edit(request, pk):
    """Edit an existing quiz with visibility/verification transitions"""
    quiz = get_object_or_404(Quiz, pk=pk)
    if quiz.creator != request.user:
        messages.error(request, 'You can only edit your own quizzes.')
        return redirect('quizzes:quiz_detail', pk=pk)
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)
        if quiz_form.is_valid():
            original_public = quiz.is_public
            quiz = quiz_form.save(commit=False)
            new_public = quiz.is_public
            # Professor editing
            if getattr(request.user, 'is_professor', False):
                if new_public:
                    quiz.verification_status = 'verified'
                    quiz.verification_by = request.user
                    quiz.verified_at = timezone.now()
                else:
                    # Private quizzes auto-verified
                    quiz.verification_status = 'verified'
                    quiz.verification_by = request.user
                    quiz.verified_at = timezone.now()
            else:
                # Student editing transitions
                if (not original_public) and new_public:
                    quiz.verification_status = 'pending'
                    quiz.verification_by = None
                    quiz.verified_at = None
                elif original_public and (not new_public):
                    # Moving to private -> auto verify if not already
                    if quiz.verification_status != 'verified':
                        quiz.verification_status = 'verified'
                        quiz.verification_by = request.user
                        quiz.verified_at = timezone.now()
            quiz.save()
            return redirect('quizzes:quiz_detail', pk=quiz.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        quiz_form = QuizForm(instance=quiz)
    return render(request, 'quizzes/quiz_edit.html', {
        'form': quiz_form,
        'quiz': quiz,
    })


@login_required
def quiz_detail(request, pk):
    """View quiz details"""
    quiz = get_object_or_404(Quiz, pk=pk)
    # Privacy: Only owner can view private quizzes
    if not quiz.is_public and quiz.creator != request.user:
        return redirect('quizzes:quiz_list')
    # Pending public quizzes: only creator or professors can view until verified
    if quiz.is_public and quiz.verification_status != 'verified' and quiz.creator != request.user and not getattr(request.user, 'is_professor', False):
        return redirect('quizzes:quiz_list')
    
    # Check if user has already attempted this quiz
    user_attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user)
    has_attempted = user_attempts.exists()
    best_attempt = user_attempts.order_by('-score').first() if has_attempted else None
    
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = QuizBookmark.objects.filter(user=request.user, quiz=quiz).exists()

    context = {
        'quiz': quiz,
        'has_attempted': has_attempted,
        'best_attempt': best_attempt,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
def quiz_attempt(request, pk):
    """Start or continue a quiz attempt"""
    quiz = get_object_or_404(Quiz, pk=pk)
    # Privacy: Only owner can attempt private quizzes
    if not quiz.is_public and quiz.creator != request.user:
        return redirect('quizzes:quiz_list')

    # Only verified quizzes can be attempted by others; creators/professors may attempt pending
    if quiz.verification_status != 'verified' and not (quiz.creator == request.user or getattr(request.user, 'is_professor', False)):
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
    """List quizzes pending verification (professors and staff only)"""
    if not (request.user.is_professor or request.user.is_staff or request.user.is_superuser):
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


@login_required
@require_http_methods(["POST"])
def approve_quiz(request, pk):
    """Approve a quiz (professors and staff only)"""
    if not (request.user.is_professor or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.verification_status = 'verified'
    quiz.verification_by = request.user
    quiz.verified_at = timezone.now()
    quiz.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    # Notification email to creator
    creator = quiz.creator
    if getattr(creator, 'email_notifications', False) and getattr(creator, 'email', ''):
        try:
            send_mail(
                subject='Your quiz has been verified',
                message=f'Your quiz "{quiz.title}" is now verified and visible to all students.',
                from_email=None,
                recipient_list=[creator.email],
                fail_silently=True,
            )
        except Exception:
            pass
    
    messages.success(request, f'"{quiz.title}" approved and published.')
    return redirect('quizzes:quiz_moderation_list')


@login_required
@require_http_methods(["POST"])
def reject_quiz(request, pk):
    """Reject a quiz (professors and staff only)"""
    if not (request.user.is_professor or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('quizzes:quiz_list')
    
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.verification_status = 'not_verified'
    quiz.verification_by = request.user
    quiz.verified_at = timezone.now()
    quiz.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    
    messages.info(request, f'"{quiz.title}" has been rejected.')
    return redirect('quizzes:quiz_moderation_list')


@login_required
@require_http_methods(["POST"])
def toggle_quiz_bookmark(request, pk):
    """Toggle bookmark for a quiz"""
    quiz = get_object_or_404(Quiz, pk=pk)
    bookmark, created = QuizBookmark.objects.get_or_create(user=request.user, quiz=quiz)
    if not created:
        bookmark.delete()
    # Redirect back
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'quizzes:quiz_list'
    return redirect(next_url)


@login_required
@require_http_methods(["POST"])
def quiz_delete(request, pk):
    """Delete a quiz (creator or professor)"""
    quiz = get_object_or_404(Quiz, pk=pk)
    if not (quiz.creator == request.user or getattr(request.user, 'is_professor', False)):
        messages.error(request, 'You do not have permission to delete this quiz.')
        return redirect('quizzes:quiz_detail', pk=pk)
    title = quiz.title
    quiz.delete()
    messages.success(request, f'Quiz "{title}" deleted.')
    return redirect('quizzes:quiz_list')

