from django.urls import path
from .views import home, upload_receipt

urlpatterns = [
    path("", home, name="home"),
    path('upload/', upload_receipt, name='upload'),
]