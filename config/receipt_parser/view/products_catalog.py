from django.db.models import Count, QuerySet, Sum, FloatField, F, OuterRef, Subquery
from django.shortcuts import render

from receipt_parser.models import StoreNames, Stores, Receipt, ReceiptItems, Items


def products_catalog_page(request):
    store_names_list: list[StoreNames]
    stores_list: list[Stores]

    stores_list = Stores.objects.annotate(
        receipt_count=Count(
            "rel_stores_id_fk",
            distinct=True,
        ),
        product_count=Count(
            "rel_stores_id_fk__rel_receipt_id_fk__item_id_fk",
            distinct=True,
        ),
    )

    context: dict = {
        "page_name": "products_catalog",
        "stores_list": stores_list,
    }

    return render(request, 'products_catalog.html', context)


def get_store_data_and_associated_products(request, store_id):
    store: Stores = Stores.objects.annotate(
        receipt_count=Count(
            "rel_stores_id_fk",
            distinct=True,
        ),
        product_count=Count(
            "rel_stores_id_fk__rel_receipt_id_fk",
            distinct=True,
        ),
    ).get(store_id=store_id)

    related_receipts: QuerySet[Receipt] = Receipt.objects.filter(store_id_fk_id=store_id)

    related_items = (
        Items.objects
        .filter(
            rel_items_id_fk__receipt_id_fk__store_id_fk_id=store_id
        )
        .annotate(
            total_quantity=Sum(
                "rel_items_id_fk__quantity"
            ),
            total_spent=Sum(
                F("rel_items_id_fk__quantity")
                * F("item_price"),
                output_field=FloatField(),
            ),
        )
        .order_by("item_name")
    )

    context: dict = {
        "store": store,
        "related_receipts": related_receipts,
        "related_items": related_items,
    }

    return render(request,
                  'components/products_catalog/store_related_products_and_receipts.html',
                  context)
