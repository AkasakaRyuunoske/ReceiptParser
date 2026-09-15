from django.urls import path

from view.dashboard import dashboard_page, receipts_for_day
from view.products_catalog import products_catalog_page, get_store_data_and_associated_products
from .views import home, stream_inference, debugg, add_receipt_page, receipts_page, receipts_storage, \
    settings_page, upload_input_image, create_receipt, load_receipt

urlpatterns = [
    path("", dashboard_page, name="home"),
    path("receipts", receipts_page, name="receipts_page"),
    path("dashboard", dashboard_page, name="dashboard_page"),
    path("receipts/day/<str:day>/", receipts_for_day, name="receipts_for_day"),
    path("receipts/add_receipt", add_receipt_page, name="add_receipt_page"),
    path("receipts/load_receipt", load_receipt, name="load_receipt"),
    path("receipts/add_receipt/upload_input_image", upload_input_image, name="upload_input_image"),
    path("receipts/add_full_receipt", create_receipt, name="create_receipt"),
    path("receipts/storage", receipts_storage, name="receipts_storage"),
    path("products_catalog", products_catalog_page, name="products_catalog_page"),
    path("products_catalog/stores/<str:store_id>/", get_store_data_and_associated_products, name="get_store_data_and_associated_products"),
    path("settings", settings_page, name="settings_page"),
    path("stream/", stream_inference, name="stream"),
    path("debugg/", debugg, name="debugg"),
]
