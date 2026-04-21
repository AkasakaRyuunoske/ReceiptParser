import base64
import datetime
import json

import requests
from django.http import StreamingHttpResponse
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
                  {'form': form, "image_path": ReceiptView.objects.last().image})

def stream_inference(request):
    def event_stream():
        url = "http://localhost:11434/api/generate"
        print(f"Stream was triggered....")
        with open(f"../config/media/{ReceiptView.objects.last().image}", "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

        response = requests.post(
            url,
            json={
                "model": "gemma4:e4b",
                "prompt": "Return a json file containing information on the image.",
                "images": [image_base64],
                "stream": True
            },
            stream=True
        )

        print(f"Stream started")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")

                print(f"Stream streamed:{chunk}")
                yield f"data: {chunk}\n\n"

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

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
