from django.urls import path
from .views import home, stream_inference, debugg

urlpatterns = [
    path("", home, name="home"),
    path("stream/", stream_inference),
    path("debugg/", debugg),
]
