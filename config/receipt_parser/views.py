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


def home(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ReceiptForm()

    return render(request, 'index.html',
                  {'form': form, "image_path": ReceiptView.objects.last().image,
                   "receipts": Receipt.objects.all()})

def debugg(request):
    inference_json = """
                    ```json{ "merchant_info": { "name": "SUPERMERCATO CONAD AFEA IRNO SRL", "address": "Corso Garibaldi, 209", "tax_id": "04827130651", "postal_city": "84081 Baronissi (SA)" }, "transaction_meta": { "document_type": "DOCUMENTO COMMERCIALE", "document_number": "2549-0013", "date": "2026-03-18", "datetime": "2026-03-18T08:48:00", "terminal_id": "07795-002-001066-0027", "item_count": 2 }, "line_items": [ { "description": "HAMBURGER TACCHINO A", "quantity": 1, "unit_price": 4.58, "tax_percentage": 10, "total_price": 2.38 } ], "financial_summary": { "subtotal": 2.16, "discount_total": 2.29, "tax_details": { "vat_total": 0.22, "vat_breakdown": [ { "percentage": 10, "amount": 0.22 } ] }, "grand_total_tax_inclusive": 2.38, "payment_info": { "payment_method": "Cash", "paid_amount": 2.38, "change_due": 0.00 } }}```
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
    inference_json_dict: dict = parse_inference_json(inference_json)

    merchant_info: dict = inference_json_dict["merchant_info"]
    transaction_info: dict = inference_json_dict["transaction_meta"]
    line_items: list = inference_json_dict["line_items"]
    payment_info: dict = inference_json_dict["financial_summary"]["payment_info"]

    store_name: StoreNames = save_store_name(merchant_info)
    store: Stores = save_store(merchant_info)
    item = save_items(line_items)
    payment_method: PaymentMethods = save_payment_method(payment_info)
    receipt_resource: ReceiptResources = save_receipt_resource(inference_json_dict)

    try:
        receipt: Receipt = Receipt.objects.get(receipt_reference=transaction_info["document_number"])
    except ObjectDoesNotExist:
        receipt = Receipt(store_id_fk=store,
                          payment_method_id_fk=payment_method,
                          receipt_resource_id_fk=receipt_resource,
                          receipt_datetime=datetime.datetime.now(),
                          receipt_reference=transaction_info["document_number"])
        receipt.save()

    receipt_item = Receipt(item_id_fk=item, receipt_id_fk=receipt)
    receipt_item.save()


def parse_inference_json(inference_json: str) -> dict:
    inference_json_dict: dict = json.loads(inference_json.replace("```json", "").replace("```", ""))

    return inference_json_dict


def save_store_name(merchant_info: dict) -> StoreNames:
    try:
        store_name: StoreNames = StoreNames.objects.get(store_name=merchant_info["name"])
    except ObjectDoesNotExist:
        store_name = StoreNames(store_name=merchant_info["name"])
        store_name.save()

    return store_name


def save_store(merchant_info: dict) -> Stores:
    store_name: StoreNames = StoreNames.objects.get(store_name=merchant_info["name"])

    try:
        store: Stores = Stores.objects.get(store_name_id_fk=store_name,
                                           address=merchant_info["address"],
                                           city=merchant_info["postal_city"], )
    except ObjectDoesNotExist:
        store = Stores(store_name_id_fk=store_name,
                       address=merchant_info["address"],
                       city=merchant_info["postal_city"], )
        store.save()

    return store


def save_items(line_items: list) -> Items:
    uncategorized: ItemCategories = ItemCategories.objects.get(item_category_name="uncategorized")

    for line_item in line_items:
        try:
            item: Items = Items.objects.get(category_id_fk=uncategorized,
                                            item_name=line_item["description"],
                                            price=line_item["unit_price"], )
        except ObjectDoesNotExist:
            item: Items = Items(category_id_fk=uncategorized,
                                item_name=line_item["description"],
                                price=line_item["unit_price"], )
            item.save()

    return item

def save_payment_method(payment_info: dict) -> PaymentMethods:
    try:
        payment_method: PaymentMethods = PaymentMethods.objects.get(
            payment_method_name=payment_info["payment_method"], )
    except ObjectDoesNotExist:
        payment_method: PaymentMethods = PaymentMethods(payment_method_name=payment_info["payment_method"], )
        payment_method.save()

    return payment_method


def save_receipt_resource(inference_json_dict: dict) -> ReceiptResources:
    try:
        receipt_resource: ReceiptResources = ReceiptResources.objects.get(
            original_image_path=f"../config/media/{ReceiptView.objects.last().image}", )
    except ObjectDoesNotExist:
        receipt_resource: ReceiptResources = ReceiptResources(
            original_image_path=f"../config/media/{ReceiptView.objects.last().image}",
            grayscale_image_path=f"../config/media/{ReceiptView.objects.last().image}",
            visualization_image_path=f"../config/media/{ReceiptView.objects.last().image}",
            raw_text_json=inference_json_dict,
        )

        receipt_resource.save()

    return receipt_resource
