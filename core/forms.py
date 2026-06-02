from django import forms
from .models import CustomOrder

class CustomOrderForm(forms.ModelForm):
    class Meta:
        model = CustomOrder
        fields = ['name', 'email', 'phone', 'description', 'reference_image', 'budget', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
