import logging

from django.shortcuts import render
from dotenv import load_dotenv

from receipt_parser.models import Receipt
from receipt_parser.services.receipts.dashboard_services import get_store_spending_pie_data, get_category_spending_pie_data, \
    get_item_spending_pie_chart, get_per_month_spending_pie_chart, get_this_week_spending_bar_chart, \
    get_calendar_spending_data, get_date_ranges_for_calendar_chart

load_dotenv()
logger = logging.getLogger(__name__)


def dashboard_page(request):
    # Dashboard charts aggregation data
    store_spending_data = get_store_spending_pie_data()
    pie_data = get_category_spending_pie_data()
    item_spending_data = get_item_spending_pie_chart()
    monthly_spending_data = get_per_month_spending_pie_chart()

    this_week_spending_data = get_this_week_spending_bar_chart()

    # Calendar charts
    calendar_spending_data, receipt_lookup = get_calendar_spending_data()
    date_ranges = get_date_ranges_for_calendar_chart()

    return render(request, 'dashboard.html',
                  context={
                      "pie_data": pie_data,
                      "store_spending_data": store_spending_data,
                      "item_spending_data": item_spending_data,
                      "monthly_spending_data": monthly_spending_data,
                      "this_week_spending_data": this_week_spending_data,
                      "calendar_spending_data": calendar_spending_data,
                      "receipt_lookup": receipt_lookup,
                      "date_ranges": date_ranges,
                      "page_name": "dashboard"
                  })


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
        "components/dashboard/receipts_for_day.html",
        {
            "day": day,
            "receipt_data": receipt_data,
        }
    )
