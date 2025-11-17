from django import forms
from .models import Deck, Card, DeckComment, DeckRating


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["title", "description", "category", "tags", "visibility"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Deck title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional description"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.TextInput(attrs={"class": "form-control", "placeholder": "Comma separated tags"}),
            "visibility": forms.RadioSelect(attrs={"class": "form-check-input"}),
        }


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["front_text", "back_text"]
        widgets = {
            "front_text": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Front content"}),
            "back_text": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Back content"}),
        }


class DeckRatingForm(forms.ModelForm):
    class Meta:
        model = DeckRating
        fields = ["stars"]
        widgets = {
            "stars": forms.Select(attrs={"class":"form-select"})
        }


class DeckCommentForm(forms.ModelForm):
    class Meta:
        model = DeckComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Share your thoughts..."})
        }
        labels = {"text":"Comment"}
