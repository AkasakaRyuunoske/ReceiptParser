from django.db.models import Count
from django.shortcuts import render

from receipt_parser.models import StoreNames, Stores


def products_catalog_page(request):
    store_names_list: list[StoreNames]
    stores_list: list[Stores]

    stores_list = Stores.objects.annotate(
        receipt_count=Count(
            "rel_stores_id_fk",
            distinct=True,
        ),
        product_count=Count(
            "rel_stores_id_fk__rel_receipt_id_fk",
            distinct=True,
        ),
    )

    context: dict = {
        "page_name": "products_catalog",
        "stores_list": stores_list,
    }

    return render(request, 'products_catalog.html', context)

def get_store_data_and_associated_products(request):

    context: dict = {

    }

    return render(request, 'products_catalog.html', context)
