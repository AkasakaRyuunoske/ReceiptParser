from django import forms
from .models import ReceiptView

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = ReceiptView
        fields = ['image']
