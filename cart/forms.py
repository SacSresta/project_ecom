# forms.py

from django import forms

class PromoCodeForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code'
        })
    )
