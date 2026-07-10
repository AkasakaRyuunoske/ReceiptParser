import base64
import datetime
import json

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from receipt_parser.forms import ReceiptImageForm
from receipt_parser.models import ReceiptImageView, StoreNames, Stores, PaymentMethods, \
    ReceiptResources, Receipt, ReceiptItems

from .forms import ReceiptForm, ReceiptItemFormSet
from .services.receipts.receipts_service import ReceiptService


def home(request):
    if request.method == 'POST':
        form = ReceiptImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ReceiptImageForm()

    image_path = ReceiptImageView.objects.last().image if not ReceiptImageView.objects.last() is None else "image_path_not_found"

    return render(request, 'index.html', context={'form': form, "image_path": image_path,
                                                  "receipts": Receipt.objects.all()})


def add_receipt_page(request):
    image_path = ReceiptImageView.objects.last().image if not ReceiptImageView.objects.last() is None else "image_path_not_found"

    try:
        raw_text_json = Receipt.objects.last().receipt_resource_id_fk.raw_text_json
    except AttributeError:
        raw_text_json = "No json yet"

    return render(request, 'add_receipt_page.html', context={"image_path": image_path,
                                                             "raw_text_json": raw_text_json,
                                                             "receipt": Receipt.objects.last()})


def dashboard_page(request):
    return render(request, 'dashboard.html', )


def receipts_page(request):
    return render(request, 'receipts.html', context={"receipts": Receipt.objects.all()})


def receipts_storage(request):
    return render(request, 'receipts_storage.html', context={"receipts": Receipt.objects.all()})


def debugg(request):
    inference_json = """
                    ```json{ "merchant_info": { "name": "H&M Hennes & Mauritz S.R.L.", "address": "Via dei Grecì 5", "tax_id": "03269110965", "postal_city": "84135 Salerno" }, "transaction_meta": { "document_type": "DOCUMENTO COMMERCIALE", "document_number": "1199-0008", "date": "2026-04-18", "datetime": "2026-04-18T11:02:00", "terminal_id": "08", "item_count": 1 }, "line_items": [ { "description": "Other Sales", "quantity": 1, "unit_price": 8.19, "tax_percentage": 22, "total_price": 9.99 } ], "financial_summary": { "subtotal": 8.19, "discount_total": 0.0, "tax_details": { "vat_total": 1.80, "vat_breakdown": [ { "percentage": 22, "amount": 1.80 } ] }, "grand_total_tax_inclusive": 9.99, "payment_info": { "payment_method": "Contanti", "paid_amount": 10.00, "change_due": 0.1 } }}```
                    
                    """
    # insert_inference_response(inference_json)
    return HttpResponse(inference_json)

def prepare_promt():
    # Loading JSON schema
    with open('receipt_parser/model_commons/schema.json') as schema_json:
        schema = json.load(schema_json)

    # Loading prompt
    with open('receipt_parser/model_commons/prompt.txt') as prompt_txt:
        prompt = prompt_txt.read()

    final_prompt: str = f"{prompt}\n\n{schema}"
    return final_prompt

def stream_inference(request):
    def event_stream():
        skip_inference: bool = True

        if not skip_inference:
            url = "http://localhost:11434/api/generate"
            print(f"Stream was triggered....")

            # Loading last updated image
            with open(f"../config/media/{ReceiptImageView.objects.last().image}", "rb") as image:
                image_base64 = base64.b64encode(image.read()).decode("utf-8")

            final_prompt: str = prepare_promt()

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
    print(f"[{datetime.datetime.now()}] Starting querying model LLAVA")
    url = "http://localhost:11434/api/generate"

    with open(f"../config/media/{ReceiptImageView.objects.last().image}", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    final_prompt = prepare_promt()

    response = requests.post(url, json={
        "model": "gemma4:e2b",
        "prompt": final_prompt,
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


def settings_page(request):
    return render(request, 'settings.html', )

def upload_input_image(request):
    form = ReceiptImageForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        image_name: str = form.cleaned_data["image"].name
        receipt_resource = ReceiptResources(original_image_path="config/config/media/receipt_parser/" + image_name,
                                            raw_text_json=inference_model())

        receipt_resource.save()
        return redirect("/receipts/add_receipt")
    else:
        print(form.errors)
        return HttpResponse(form.errors)

def post_receipt(request):
    form = ReceiptImageForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return redirect("/receipts/add_receipt")
    else:
        print(form.errors)
        return HttpResponse(form.errors)

@transaction.atomic
def create_receipt(request):

    if request.method == "POST":

        receipt_form = ReceiptForm(request.POST)
        receipt_form_data = receipt_form.data
        item_formset = None

        if receipt_form.is_valid():

            store_name = receipt_form_data['store_id_fk']

            store_name_obj, _ = StoreNames.objects.get_or_create(
                store_name=store_name
            )

            store_obj, _ = Stores.objects.get_or_create(
                store_name_id_fk=store_name_obj
            )

            receipt_resource = ReceiptResources.objects.last()
            # receipt_resource.save()

            receipt = receipt_form.save(commit=False)

            receipt.receipt_resource_id_fk = receipt_resource
            receipt.store_id_fk = store_obj
            receipt.save()

            item_formset = ReceiptItemFormSet(
                request.POST,
                instance=receipt
            )

            if item_formset.is_valid():
                item_formset.save()

                return render(request, "add_receipt_page.html")

    else:
        receipt_form = ReceiptForm()
        item_formset = ReceiptItemFormSet()

    return render(
        request,
        "add_receipt_page.html",
        {
            "receipt_form": receipt_form,
            "item_formset": item_formset
        }
    )
