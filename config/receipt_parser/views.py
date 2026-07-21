import base64
import datetime
import json
import os
import re

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDate, ExtractYear
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from receipt_parser.forms import ReceiptImageForm
from receipt_parser.models import ReceiptImageView, StoreNames, Stores, PaymentMethods, \
    ReceiptResources, Receipt, ReceiptItems, ItemCategories, Items

from .forms import ReceiptForm
from .services.receipts.receipts_service import ReceiptService

load_dotenv()


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
                                                             "receipt": Receipt.objects.last(),
                                                             "page_name": "receipts.add_receipt",
                                                             })


def dashboard_page(request):
    store_spending_data = get_store_spending_pie_data()
    pie_data = get_category_spending_pie_data()
    item_spending_data = get_item_spending_pie_chart()
    monthly_spending_data = get_per_month_spending_pie_chart()

    calendar_spending_data, receipt_lookup = get_calendar_spending_data()

    date_ranges = get_date_ranges_for_calendar_chart()

    return render(request, 'dashboard.html',
                  context={
                      "pie_data": pie_data,
                      "store_spending_data": store_spending_data,
                      "item_spending_data": item_spending_data,
                      "monthly_spending_data": monthly_spending_data,
                      "calendar_spending_data": calendar_spending_data,
                      "receipt_lookup": receipt_lookup,
                      "date_ranges": date_ranges,
                      "page_name": "dashboard"
                  })


def get_date_ranges_for_calendar_chart() -> dict:
    latest_date = Receipt.objects.order_by('-receipt_datetime').first().receipt_datetime
    newest_date = Receipt.objects.order_by('-receipt_datetime').last().receipt_datetime

    years = Receipt.objects.annotate(
        year=ExtractYear('receipt_datetime')
    ).values('year').distinct()

    year_list = list(years.values_list('year', flat=True))
    # adapted_year_list = list()
    #
    # for year in year_list:
    #     adapted_year_list.append(f"{year}-01")
    #     adapted_year_list.append(f"{year}-12")

    date_ranges: dict = {
        "latest_receipt": latest_date,
        "newest_date": newest_date,
        "years": year_list,
    }

    return date_ranges


def receipts_for_day(request, day):
    receipts = (
        Receipt.objects
        .filter(receipt_datetime__date=day)
        .select_related(
            "store_id_fk__store_name_id_fk",
            "payment_method_id_fk"
        )
        .prefetch_related("rel_receipt_id_fk__item_id_fk")
        .order_by("-receipt_datetime")
    )

    receipt_data = []

    for receipt in receipts:
        total = sum(
            ri.quantity * ri.price
            for ri in receipt.rel_receipt_id_fk.all()
        )

        receipt_data.append({
            "receipt": receipt,
            "total": total,
        })

    return render(
        request,
        "components/receipts_for_day.html",
        {
            "day": day,
            "receipt_data": receipt_data,
        }
    )


def get_calendar_spending_data():
    line_total = ExpressionWrapper(
        F("quantity") * F("price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    daily_data = (
        ReceiptItems.objects
        .annotate(
            day=TruncDate("receipt_id_fk__receipt_datetime")
        )
        .values("day")
        .annotate(
            total=Sum(line_total)
        )
        .order_by("day")
    )

    receipt_lookup = {}

    for row in daily_data:
        receipt_lookup[row["day"].isoformat()] = {
            "total": float(row["total"])
        }

    calendar_data = [
        [
            row["day"].isoformat(),
            float(row["total"])
        ]
        for row in daily_data
    ]

    return calendar_data, receipt_lookup


def get_category_spending_pie_data():
    category_spending = (
        ReceiptItems.objects
        .values(
            category=F("item_id_fk__category_id_fk__item_category_name")
        )
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        .order_by("-total")
    )

    pie_data = [
        {
            "name": row["category"],
            "value": float(row["total"])
        }
        for row in category_spending
    ]

    return pie_data


def get_store_spending_pie_data():
    store_spending = (
        ReceiptItems.objects
        .values(
            store=F(
                "receipt_id_fk__store_id_fk__store_name_id_fk__store_name"
            )
        )
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        .order_by("-total")
    )

    store_spending_data = [
        {
            "name": row["store"],
            "value": float(row["total"])
        }
        for row in store_spending
    ]

    return store_spending_data


def get_item_spending_pie_chart():
    item_spending = (
        ReceiptItems.objects
        .values(
            item=F("item_id_fk__item_name")
        )
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        .order_by("-total")[:10]
    )

    item_spending_data = [
        {
            "name": row["item"],
            "value": float(row["total"])
        }
        for row in item_spending
    ]

    return item_spending_data


def get_per_month_spending_pie_chart():
    monthly_spending = (
        ReceiptItems.objects
        .annotate(
            month=TruncMonth(
                "receipt_id_fk__receipt_datetime"
            )
        )
        .values("month")
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        .order_by("month")
    )

    monthly_spending_data = [
        {
            "name": row["month"].strftime('%Y-%m-%d'),
            "value": float(row["total"])
        }
        for row in monthly_spending
    ]

    return monthly_spending_data


def receipts_page(request):
    return render(request, 'receipts.html',
                  context={
                      "receipts": Receipt.objects.all(),
                      "page_name": "receipts.storage",
                  })


def receipts_storage(request):
    return render(request, 'receipts_storage.html',
                  context={
                      "receipts": Receipt.objects.all(),
                      "page_name": "receipts.storage",
                  })


def debugg(request):
    inference_json = """
                    ```json{ "merchant_info": 
                    { "name": "H&M Hennes & Mauritz S.R.L.", "address": "Via dei Grecì 5",
                     "tax_id": "03269110965", "postal_city": "84135 Salerno" }, 
                     "transaction_meta": { "document_type": "DOCUMENTO COMMERCIALE", 
                     "document_number": "1199-0008", "date": "2026-04-18", 
                     "datetime": "2026-04-18T11:02:00", "terminal_id": "08", "item_count": 1 }, 
                     "line_items": [ { "description": "Other Sales", "quantity": 1, 
                     "unit_price": 8.19, "tax_percentage": 22, "total_price": 9.99 } ], 
                     "financial_summary": { "subtotal": 8.19, "discount_total": 0.0, 
                     "tax_details": { "vat_total": 1.80, "vat_breakdown": 
                     [ { "percentage": 22, "amount": 1.80 } ] }, 
                     "grand_total_tax_inclusive": 9.99, "payment_info": 
                     { "payment_method": "Contanti", "paid_amount": 10.00, "change_due": 0.1 
                     } 
                     }}
                     ```
                    
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
            url = os.getenv("MODEL_BACKEND_URL", "http://localhost:11434/api/generate")
            print(f"Stream was triggered....")

            # Loading last updated image
            with open(f"../config/media/{ReceiptImageView.objects.last().image}", "rb") as image:
                image_base64 = base64.b64encode(image.read()).decode("utf-8")

            final_prompt: str = prepare_promt()

            response = requests.post(
                url,
                json={
                    "model": os.getenv("MODEL_NAME", "gemma4:e4b"),
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
    url = os.getenv("MODEL_BACKEND_URL", "http://localhost:11434/api/generate")

    with open(f"../config/media/{ReceiptImageView.objects.last().image}", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    final_prompt = prepare_promt()

    response = requests.post(url, json={
        "model": os.getenv("MODEL_NAME", "gemma4:e4b"),
        "prompt": final_prompt,
        "images": [image_base64],
        "stream": False,
    })

    print(f"[{datetime.datetime.now()}] Got response from the model")
    print(response.json()["response"])

    response_json = response.json()["response"]
    response_json = response_json.replace("```json", "").replace("```", "")

    return response_json


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

    for i, item in enumerate(items):
        receipt_item: ReceiptItems = ReceiptItems(item_id_fk=item, receipt_id_fk=receipt,
                                                  price=line_items[i]["unit_price"])
        receipt_item.save()


def settings_page(request):
    return render(request, 'settings.html', )


def upload_input_image(request):
    form = ReceiptImageForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()

        inference_response = inference_model()
        insert_inference_response(inference_response)

        receipt_resource = ReceiptResources(original_image_path=ReceiptImageView.objects.last().image.url,
                                            raw_text_json=inference_response)

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
        receipt_reference = request.POST.get("receipt_reference", "").strip()

        existing_receipt = Receipt.objects.filter(
            receipt_reference=receipt_reference
        ).first()

        receipt_form = ReceiptForm(request.POST, instance=existing_receipt)

        if receipt_form.is_valid():
            store_name = receipt_form.cleaned_data["store_id_fk"]
            store_name_obj, _ = StoreNames.objects.get_or_create(store_name=store_name)
            store_obj, _ = Stores.objects.get_or_create(store_name_id_fk=store_name_obj)
            receipt_resource = ReceiptResources.objects.last()

            receipt = receipt_form.save(commit=False)
            receipt.receipt_resource_id_fk = receipt_resource
            receipt.store_id_fk = store_obj
            receipt.save()

            if existing_receipt:
                ReceiptItems.objects.filter(receipt_id_fk=receipt).delete()

            row_pattern = re.compile(r"^item_name_(?:new_)?(\d+)$")
            indices = [
                int(m.group(1))
                for key in request.POST
                if (m := row_pattern.match(key))
            ]

            request_row_pattern = re.compile(r"^item_name_(new_)?(\d+)$")

            for key in request.POST:
                m = request_row_pattern.match(key)
                if not m:
                    continue

                is_new = m.group(1) is not None
                index = m.group(2)

                prefix = "item_name_new_" if is_new else "item_name_"

                item_name = request.POST.get(f"{prefix}{index}", "").strip()
                if not item_name:
                    continue

                if is_new:
                    category_name = request.POST.get(f"item_category_name_new_{index}", "").strip()
                    category_description = request.POST.get(f"item_category_description_new_{index}", "")
                    qty = int(request.POST.get(f"item_qty_new_{index}", 1) or 1)
                    unit_price = float(request.POST.get(f"item_unit_price_new_{index}", 0) or 0)
                else:
                    category_name = request.POST.get(f"item_category_name_{index}", "").strip()
                    category_description = request.POST.get(f"item_category_description_{index}", "")
                    qty = int(request.POST.get(f"item_qty_{index}", 1) or 1)
                    unit_price = float(request.POST.get(f"item_unit_price_{index}", 0) or 0)

                category_obj, _ = ItemCategories.objects.get_or_create(
                    item_category_name=category_name,
                    defaults={"item_category_description": category_description},
                )

                item_obj, _ = Items.objects.get_or_create(
                    item_name=item_name,
                    category_id_fk=category_obj,
                )

                ReceiptItems.objects.create(
                    item_id_fk=item_obj,
                    receipt_id_fk=receipt,
                    quantity=qty,
                    price=unit_price,
                )

            return render(request, "add_receipt_page.html")

    else:
        receipt_form = ReceiptForm()

    return render(request, "add_receipt_page.html", {"receipt_form": receipt_form})
