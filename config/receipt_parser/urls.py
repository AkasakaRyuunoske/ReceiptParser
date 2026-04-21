from django.urls import path
from .views import home, stream_inference

urlpatterns = [
    path("", home, name="home"),
    path("stream/", stream_inference),
]
