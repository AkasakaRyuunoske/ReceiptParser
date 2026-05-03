from django.urls import path
from .views import home, stream_inference, debugg, add_receipt_page, receipts_page, receipts_storage, dashboard_page, settings_page

urlpatterns = [
    path("", home, name="home"),
    path("receipts", receipts_page, name="receipts_page"),
    path("dashboard", dashboard_page, name="dashboard_page"),
    path("receipts/add_receipt", add_receipt_page, name="add_receipt_page"),
    path("receipts/storage", receipts_storage, name="receipts_storage"),
    path("settings", settings_page, name="settings_page"),
    path("stream/", stream_inference),
    path("debugg/", debugg),
]
