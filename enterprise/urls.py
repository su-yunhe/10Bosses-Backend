from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", search_enterprise),
    path("hello", hello),
]
