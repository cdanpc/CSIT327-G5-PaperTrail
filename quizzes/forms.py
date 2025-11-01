from django import forms
from .models import Quiz, Question, Option, QuizAttempt, QuizAttemptAnswer


class QuizForm(forms.ModelForm):
    """Form for creating/editing a quiz"""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quiz title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe this quiz...',
                'rows': 3
            }),
        }


class QuestionForm(forms.Form):
    """Form for a single question"""
    
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your question here...',
            'rows': 3
        })
    )
    question_type = forms.ChoiceField(
        choices=Question.QUESTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    correct_answer = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter correct answer'
        })
    )
    # For multiple choice options
    option_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}))
    option_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 2'}))
    option_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 3'}))
    option_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 4'}))


class QuizAttemptForm(forms.Form):
    """Form for answering a quiz question"""
    
    answer = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer...'
        })
    )
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        if question.question_type == 'multiple_choice':
            # Use radio buttons for multiple choice
            options = list(question.options.all().order_by('order'))
            choices = [(opt.id, opt.option_text) for opt in options]
            self.fields['answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True
            )
            self.fields['answer'].label = ''
        else:
            # Text input for fill in the blank
            self.fields['answer'] = forms.CharField(
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your answer...'
                }),
                required=True
            )
            self.fields['answer'].label = ''

