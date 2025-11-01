from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Quiz(models.Model):
    """Quiz model with verification status similar to Resource"""
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    
    # Approval and verification
    verification_status = models.CharField(
        max_length=15,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    verification_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_quizzes'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    attempts_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    def increment_attempts_count(self):
        """Increment attempts count"""
        self.attempts_count += 1
        self.save(update_fields=['attempts_count'])


class Question(models.Model):
    """Question model for quizzes"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_in_blank', 'Fill in the Blank'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    correct_answer = models.CharField(max_length=500, help_text='For multiple choice: option text. For fill in blank: answer text')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}"


class Option(models.Model):
    """Options for multiple choice questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.question.quiz.title} - {self.option_text}"


class QuizAttempt(models.Model):
    """Record of a student attempting a quiz"""
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.get_display_name()} - {self.quiz.title}"
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 2)
    
    def is_completed(self):
        """Check if attempt is completed"""
        return self.completed_at is not None


class QuizAttemptAnswer(models.Model):
    """Individual answer for each question in a quiz attempt"""
    
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.student.get_display_name()} - {self.question.question_text[:50]}"

