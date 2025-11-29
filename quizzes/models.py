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
    
    # Privacy
    is_public = models.BooleanField(default=True, help_text='If True, visible to all users. If False, only visible to creator.')
    
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


class QuizBookmark(models.Model):
    """User bookmarks for quizzes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_bookmarks')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'quiz']
        ordering = ['-created_at']


class QuizRating(models.Model):
    """User ratings for quizzes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_ratings')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        help_text='Rating from 1 to 5 stars'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'quiz']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} rated {self.quiz.title} - {self.stars} stars"


class QuizComment(models.Model):
    """User comments on quizzes with threading support"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_comments')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(help_text='Comment text')
    
    # Threading support - allows replies to comments
    parent_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']  # Chronological for threading
        indexes = [
            models.Index(fields=['quiz', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} on {self.quiz.title}"
    
    def is_owner_comment(self):
        """Check if comment author is the quiz creator"""
        return self.user == self.quiz.creator
    
    def get_reply_count(self):
        """Get number of direct replies"""
        return self.replies.count()


class QuizLike(models.Model):
    """User likes for quizzes - replaces attempts counter"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_likes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'quiz']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quiz', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} likes {self.quiz.title}"

