from django import forms
from django.forms import inlineformset_factory

from .models import ReceiptImageView, Receipt, ReceiptItems


class ReceiptImageForm(forms.ModelForm):
    class Meta:
        model = ReceiptImageView
        fields = ['image']


class ReceiptForm(forms.ModelForm):
    store_id_fk = forms.CharField()

    class Meta:
        model = Receipt
        fields = [
            "payment_method_id_fk",
            "receipt_datetime",
            "receipt_description",
        ]


class ReceiptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItems
        fields = [
            "item_id_fk",
        ]


ReceiptItemFormSet = inlineformset_factory(
    Receipt,
    ReceiptItems,
    fields=["item_id_fk"],
    extra=1,
    can_delete=True
)
