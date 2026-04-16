from django import forms
from .models import Receipt

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['image']
