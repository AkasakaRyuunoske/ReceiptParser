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

        schema = {
              "title": "Retail Sales Receipt Schema",
              "description": "Schema designed to capture structured data from a typical Italian retail receipt (Supermercato).",
              "type": "object",
              "properties": {
                "merchant_info": {
                  "description": "Information about the store and the merchant.",
                  "type": "object",
                  "properties": {
                    "name": {
                      "type": "string",
                      "description": "Name of the supermarket/merchant."
                    },
                    "address": {
                      "type": "string",
                      "description": "Physical address of the store."
                    },
                    "tax_id": {
                      "type": "string",
                      "description": "Partita IVA (VAT ID) of the merchant."
                    },
                    "postal_city": {
                      "type": "string",
                      "description": "Postal code and city."
                    }
                  },
                  "required": ["name", "address", "tax_id"]
                },
                "transaction_meta": {
                  "description": "Metadata about the sale.",
                  "type": "object",
                  "properties": {
                    "document_type": {
                      "type": "string",
                      "description": "Type of document (e.g., DOCUMENTO COMMERCIALE)."
                    },
                    "document_number": {
                      "type": "string",
                      "description": "The unique number assigned to the transaction."
                    },
                    "date": {
                      "type": "string",
                      "format": "date",
                      "description": "Date of the transaction (YYYY-MM-DD)."
                    },
                    "datetime": {
                      "type": "string",
                      "format": "date-time",
                      "description": "Full date and time of the transaction."
                    },
                    "terminal_id": {
                      "type": "string",
                      "description": "The cash register or terminal ID used for the sale."
                    },
                    "item_count": {
                      "type": "integer",
                      "description": "The total number of items counted at the time of sale."
                    }
                  },
                  "required": ["document_number", "datetime"]
                },
                "line_items": {
                  "description": "An array of goods or services sold.",
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "description": {
                        "type": "string",
                        "description": "Detailed description of the item (e.g., HAMBURGER TACCHINO A)."
                      },
                      "quantity": {
                        "type": "number",
                        "description": "The quantity purchased."
                      },
                      "unit_price": {
                        "type": "number",
                        "description": "The price per single unit (pre-tax)."
                      },
                      "tax_percentage": {
                        "type": "number",
                        "description": "The VAT percentage applied (e.g., 10%)."
                      },
                      "total_price": {
                        "type": "number",
                        "description": "The final total price for this specific item (Quantity * Unit Price)."
                      }
                    },
                    "required": ["description", "quantity", "unit_price", "total_price"]
                  }
                },
                "financial_summary": {
                  "description": "The financial totals and payments.",
                  "type": "object",
                  "properties": {
                    "subtotal": {
                      "type": "number",
                      "description": "The total price of all goods before taxes and discounts (Subtotal)."
                    },
                    "discount_total": {
                      "type": "number",
                      "description": "The total amount deducted via discounts (e.g., ALTRI SCONTI)."
                    },
                    "tax_details": {
                      "type": "object",
                      "properties": {
                        "vat_total": {
                          "type": "number",
                          "description": "The total amount of VAT/IVA paid."
                        },
                        "vat_breakdown": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                              "percentage": {"type": "number"},
                              "amount": {"type": "number"}
                            }
                          }
                        }
                      },
                      "required": ["vat_total"]
                    },
                    "grand_total_tax_inclusive": {
                      "type": "number",
                      "description": "The final required cost after taxes and discounts (TOT. COMPLESSIVO)."
                    },
                    "payment_info": {
                      "type": "object",
                      "properties": {
                        "payment_method": {
                          "type": "string",
                          "description": "Method of payment (e.g., Cash, Card)."
                        },
                        "paid_amount": {
                          "type": "number",
                          "description": "The actual amount paid by the customer."
                        },
                        "change_due": {
                          "type": "number",
                          "description": "The change received (if applicable)."
                        }
                      },
                      "required": ["paid_amount"]
                    }
                  }
                }
              },
              "required": ["merchant_info", "transaction_meta", "line_items", "financial_summary"]
            }
        response = requests.post(
            url,
            json={
                "model": "gemma4:e4b",
                "prompt": f"Return a json file containing information on the image following this json schema: {schema}",
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
