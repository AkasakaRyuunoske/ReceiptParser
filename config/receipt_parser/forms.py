from django import forms
from .models import ReceiptImageView, Receipt


class ReceiptImageForm(forms.ModelForm):
    class Meta:
        model = ReceiptImageView
        fields = ['image']


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = [
                    'image', 'store_name', 'store_address', 'store_city',
                    'receipt_datetime', 'receipt_reference', 'item_name', 'item_category_name',
                    'item_category_description', 'item_qty', 'item_unit_price', 'item_total_price',
        ]
