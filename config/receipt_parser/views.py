import base64
import datetime
import json

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect
from receipt_parser.forms import ReceiptForm
from receipt_parser.models import ReceiptView, StoreNames, Stores, Items, ItemCategories, PaymentMethods, \
    ReceiptResources, Receipt, ReceiptItems

from .services.receipts.receipts_service import ReceiptService


def home(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ReceiptForm()

    image_path = ReceiptView.objects.last().image if not ReceiptView.objects.last() is None else "image_path_not_found"

    return render(request, 'index.html',
                  {'form': form, "image_path": image_path,
                   "receipts": Receipt.objects.all()})

def debugg(request):
    inference_json = """
                    ```json{ "merchant_info": { "name": "H&M Hennes & Mauritz S.R.L.", "address": "Via dei Grecì 5", "tax_id": "03269110965", "postal_city": "84135 Salerno" }, "transaction_meta": { "document_type": "DOCUMENTO COMMERCIALE", "document_number": "1199-0008", "date": "2026-04-18", "datetime": "2026-04-18T11:02:00", "terminal_id": "08", "item_count": 1 }, "line_items": [ { "description": "Other Sales", "quantity": 1, "unit_price": 8.19, "tax_percentage": 22, "total_price": 9.99 } ], "financial_summary": { "subtotal": 8.19, "discount_total": 0.0, "tax_details": { "vat_total": 1.80, "vat_breakdown": [ { "percentage": 22, "amount": 1.80 } ] }, "grand_total_tax_inclusive": 9.99, "payment_info": { "payment_method": "Contanti", "paid_amount": 10.00, "change_due": 0.1 } }}```
                    
                    """
    insert_inference_response(inference_json)
    return HttpResponse("")

def stream_inference(request):
    def event_stream():
        skip_inference: bool = True
        if not skip_inference:
            url = "http://localhost:11434/api/generate"
            print(f"Stream was triggered....")

            # Loading last updated image
            with open(f"../config/media/{ReceiptView.objects.last().image}", "rb") as image:
                image_base64 = base64.b64encode(image.read()).decode("utf-8")

            # Loading JSON schema
            with open('receipt_parser/model_commons/schema.json') as schema_json:
                schema = json.load(schema_json)

            # Loading prompt
            with open('receipt_parser/model_commons/prompt.txt') as prompt_txt:
                prompt = prompt_txt.read()

            final_prompt = f"{prompt}\n\n{schema}"

            response = requests.post(
                url,
                json={
                    "model": "gemma4:e4b",
                    "prompt": final_prompt,
                    "images": [image_base64],
                    "stream": True
                },
                stream=True
            )

            response_buffer = ""

            print(f"Stream started")
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("response", "")

                    print(f"Stream streamed:{chunk}")
                    response_buffer += chunk
                    yield f"data: {chunk}\n\n"

                    if data.get("done"):
                        print("Stream finished")
                        print("FINAL:", insert_inference_response(response_buffer))

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


def insert_inference_response(inference_json: str) -> None:
    receipt_service: ReceiptService = ReceiptService()

    inference_json_dict: dict = receipt_service.parse_inference_json(inference_json)

    merchant_info: dict = inference_json_dict["merchant_info"]
    transaction_info: dict = inference_json_dict["transaction_meta"]
    line_items: list = inference_json_dict["line_items"]
    payment_info: dict = inference_json_dict["financial_summary"]["payment_info"]

    store_name: StoreNames = receipt_service.save_store_name(merchant_info)
    store: Stores = receipt_service.save_store(merchant_info)
    items = receipt_service.save_items(line_items)
    payment_method: PaymentMethods = receipt_service.save_payment_method(payment_info)
    receipt_resource: ReceiptResources = receipt_service.save_receipt_resource(inference_json_dict)

    try:
        receipt: Receipt = Receipt.objects.get(receipt_reference=transaction_info["document_number"])
    except ObjectDoesNotExist:
        receipt_datetime = datetime.datetime.fromisoformat(transaction_info["datetime"])
        receipt = Receipt(store_id_fk=store,
                          payment_method_id_fk=payment_method,
                          receipt_resource_id_fk=receipt_resource,
                          receipt_datetime=receipt_datetime,
                          receipt_reference=transaction_info["document_number"])
        receipt.save()
        receipt: Receipt = Receipt.objects.get(receipt_reference=transaction_info["document_number"])

    for item in items:
        receipt_item: ReceiptItems = ReceiptItems(item_id_fk=item, receipt_id_fk=receipt)
        receipt_item.save()
