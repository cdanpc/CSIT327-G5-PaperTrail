from django import forms
from .models import Deck, Card


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Deck title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional description"}),
        }


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["front_text", "back_text"]
        widgets = {
            "front_text": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Front content"}),
            "back_text": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Back content"}),
        }
