from django.urls import path
from .views import home, stream_inference, debugg, add_receipt_page, receipts_page, receipts_storage, dashboard_page, \
    settings_page, upload_input_image, create_receipt

urlpatterns = [
    path("", home, name="home"),
    path("receipts", receipts_page, name="receipts_page"),
    path("dashboard", dashboard_page, name="dashboard_page"),
    path("receipts/add_receipt", add_receipt_page, name="add_receipt_page"),
    path("receipts/add_receipt/upload_input_image", upload_input_image, name="upload_input_image"),
    path("receipts/add_full_receipt", create_receipt, name="create_receipt"),
    path("receipts/storage", receipts_storage, name="receipts_storage"),
    path("settings", settings_page, name="settings_page"),
    path("stream/", stream_inference, name="stream"),
    path("debugg/", debugg, name="debugg"),
]
