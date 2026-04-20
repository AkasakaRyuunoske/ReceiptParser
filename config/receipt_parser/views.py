import base64
import datetime

import requests
from django.shortcuts import render, redirect
from receipt_parser.forms import ReceiptForm
from receipt_parser.models import ReceiptView


def home(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ReceiptForm()

    return render(request, 'index.html',
                  {'form': form, "model_response": inference_model(), "image_path": ReceiptView.objects.last().image})


def inference_model():
    print(f"[{datetime.datetime.now()}]Starting querying model LLAVA")
    url = "http://localhost:11434/api/generate"

    with open(f"../config/media/{ReceiptView.objects.last().image}", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(url, json={
        "model": "gemma4:e4b",
        "prompt": "Return a json file containing information on the image.",
        "images": [image_base64],
        "stream": False,
    })

    print(f"[{datetime.datetime.now()}] Got response from the model")
    print(response.json()["response"])

    return response.json()["response"]
