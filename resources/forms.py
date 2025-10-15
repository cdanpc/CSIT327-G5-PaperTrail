from django import forms
from .models import Resource, Tag


class ResourceUploadForm(forms.ModelForm):
    """Form for uploading resources"""
    
    file = forms.FileField(
        required=False,
        help_text='Upload a file (PDF, PPT, DOCX, etc.) - Max 5MB',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.ppt,.pptx,.doc,.docx,.txt,.jpg,.jpeg,.png'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Select relevant tags for this resource'
    )
    
    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'file', 'external_url', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe this resource...',
                'rows': 4
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'external_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com (optional if uploading file)'
            }),
        }
    
    def clean(self):
        """Validate that either file or external URL is provided"""
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        external_url = cleaned_data.get('external_url')
        
        # Handle N/A values
        if external_url and str(external_url).lower().strip() in ['n/a', 'na', 'none', '']:
            cleaned_data['external_url'] = None
            external_url = None
        
        # At least one must be provided
        if not file and not external_url:
            raise forms.ValidationError(
                'Please either upload a file or provide an external URL.'
            )
        
        # File size validation (5MB = 5242880 bytes)
        if file and file.size > 5242880:
            raise forms.ValidationError(
                'File size must not exceed 5MB.'
            )
        
        return cleaned_data


class ResourceSearchForm(forms.Form):
    """Form for searching resources"""
    
    q = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search resources...'
        })
    )
    
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label='All Tags',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    resource_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Resource.RESOURCE_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
