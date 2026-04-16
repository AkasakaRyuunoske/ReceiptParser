from django.shortcuts import render, redirect

from receipt_parser.forms import ReceiptForm


def home(request):
    return render(request, "index.html")

def upload_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ReceiptForm()

    return render(request, 'upload.html', {'form': form})
