# dashboard/forms.py
from django import forms
from .models import StudentProfile
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    
    class Meta:
        model = StudentProfile
        fields = [
            'attempt_year', 
            'neet_exam_date',
            'batch_enrolled',
            'mentor',  # CHANGED FROM 'mentor_assigned'
            'phone', 
            'address',
            'profile_picture'
        ]
        # REMOVED: 'mentor_qualification' from fields
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Add date picker for neet_exam_date
        self.fields['neet_exam_date'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update user information
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile