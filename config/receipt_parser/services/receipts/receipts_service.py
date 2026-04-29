import base64
import json

from django.core.exceptions import ObjectDoesNotExist
from pydantic import BaseModel
from receipt_parser.models import ReceiptView, StoreNames, Stores, Items, ItemCategories, PaymentMethods, \
    ReceiptResources


class ReceiptService(BaseModel):
    def parse_inference_json(self, inference_json: str) -> dict:
        inference_json_dict: dict = json.loads(inference_json.replace("```json", "").replace("```", ""))

        return inference_json_dict

    def save_store_name(self, merchant_info: dict) -> StoreNames:
        try:
            store_name: StoreNames = StoreNames.objects.get(store_name=merchant_info["name"])
        except ObjectDoesNotExist:
            store_name = StoreNames(store_name=merchant_info["name"])
            store_name.save()
            store_name: StoreNames = StoreNames.objects.get(store_name=merchant_info["name"])

        return store_name

    def save_store(self, merchant_info: dict) -> Stores:
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
            store: Stores = Stores.objects.get(store_name_id_fk=store_name,
                                               address=merchant_info["address"],
                                               city=merchant_info["postal_city"], )
        return store

    def save_items(self, line_items: list) -> list[Items]:
        uncategorized: ItemCategories = ItemCategories.objects.get(item_category_name="uncategorized")

        items: list[Items] = list()
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
                item: Items = Items.objects.get(category_id_fk=uncategorized,
                                                item_name=line_item["description"],
                                                price=line_item["unit_price"], )

            items.append(item)

        return items

    def save_payment_method(self, payment_info: dict) -> PaymentMethods:
        try:
            payment_method: PaymentMethods = PaymentMethods.objects.get(
                payment_method_name=payment_info["payment_method"], )
        except ObjectDoesNotExist:
            payment_method: PaymentMethods = PaymentMethods(payment_method_name=payment_info["payment_method"], )
            payment_method.save()
            payment_method: PaymentMethods = PaymentMethods.objects.get(
                payment_method_name=payment_info["payment_method"], )

        return payment_method

    def save_receipt_resource(self, inference_json_dict: dict) -> ReceiptResources:
        try:
            receipt_resource: ReceiptResources = ReceiptResources.objects.get(
                original_image_path=f"{ReceiptView.objects.last().image}", )
        except ObjectDoesNotExist:
            receipt_resource: ReceiptResources = ReceiptResources(
                original_image_path=f"{ReceiptView.objects.last().image}",
                grayscale_image_path=f"{ReceiptView.objects.last().image}",
                visualization_image_path=f"{ReceiptView.objects.last().image}",
                raw_text_json=inference_json_dict,
            )

            receipt_resource.save()
            receipt_resource: ReceiptResources = ReceiptResources.objects.get(
                original_image_path=f"{ReceiptView.objects.last().image}", )

        return receipt_resource
