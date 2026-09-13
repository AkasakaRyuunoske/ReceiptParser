import datetime
import logging

from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDate, ExtractYear
from dotenv import load_dotenv

from receipt_parser.models import Receipt, ReceiptItems

load_dotenv()
logger = logging.getLogger(__name__)


def get_date_ranges_for_calendar_chart() -> dict:
    latest_receipt = Receipt.objects.order_by('-receipt_datetime').first()
    newest_receipt = Receipt.objects.order_by('-receipt_datetime').last()

    latest_date = None
    newest_date = None
    year_list = None

    if latest_receipt is not None:
        latest_date = latest_receipt.receipt_datetime
        newest_date = newest_receipt.receipt_datetime

        years = Receipt.objects.annotate(
            year=ExtractYear('receipt_datetime')
        ).values('year').distinct()

        year_list = list(years.values_list('year', flat=True))

    date_ranges: dict = {
        "latest_receipt": latest_date,
        "newest_date": newest_date,
        "years": year_list,
    }

    return date_ranges


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


def get_this_week_spending_bar_chart():
    start = datetime.datetime.now() - datetime.timedelta(days=6)
    end = start + datetime.timedelta(days=7)

    weekly_spending = (
        ReceiptItems.objects
        .filter(
            receipt_id_fk__receipt_datetime__range=(start, end)
        )
        .annotate(
            day=TruncDate("receipt_id_fk__receipt_datetime")
        )
        .values("day")
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        .order_by("day")
    )

    weekly_spending_data = [
        {
            "name": row["day"].strftime('%Y-%m-%d'),
            "value": float(row["total"])
        }
        for row in weekly_spending
    ]

    return weekly_spending_data


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
