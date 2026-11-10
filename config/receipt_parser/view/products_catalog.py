from django.db.models import Count, QuerySet, Sum, FloatField, F, OuterRef, Subquery, Prefetch
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from receipt_parser.models import StoreNames, Stores, Receipt, ReceiptItems, Items
from services.receipts.dashboard_services import get_date_ranges_for_calendar_chart, get_calendar_spending_data, \
    get_calendar_spending_data_by_item


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

def get_product_overview(request, product_id):
    related_item = (
        Items.objects
        .annotate(
            total_quantity=Sum("rel_items_id_fk__quantity"),
            total_spent=Sum(
                F("rel_items_id_fk__quantity") * F("item_price"),
                output_field=FloatField(),
            ),
        )
        .prefetch_related(
            Prefetch(
                "rel_items_id_fk",
                queryset=ReceiptItems.objects
                .select_related("receipt_id_fk")
                .order_by("-receipt_id_fk__receipt_datetime"),
                to_attr="receipt_items",
            )
        )
        .get(item_id=product_id)
    )

    receipts = [
        receipt_item.receipt_id_fk
        for receipt_item in related_item.receipt_items
    ]

    most_recent_receipt = (
        related_item.receipt_items[0]
        if related_item.receipt_items else None
    ).receipt_id_fk

    oldest_receipt = (
        related_item.receipt_items[-1]
        if related_item.receipt_items else None
    ).receipt_id_fk

    related_stores = {
        receipt_item.receipt_id_fk.store_id_fk
        for receipt_item in related_item.receipt_items
    }

    date_ranges = get_date_ranges_for_calendar_chart(most_recent_receipt, oldest_receipt)

    calendar_spending_data, receipt_lookup = get_calendar_spending_data_by_item(related_item)

    context: dict = {
        "related_item": related_item,
        "related_receipts": receipts,
        "related_stores": related_stores,
        "date_ranges": date_ranges,
        "calendar_spending_data": calendar_spending_data,
        "receipt_lookup": receipt_lookup,
    }

    return render(request, 'components/products_catalog/product_overview_page.html', context)
