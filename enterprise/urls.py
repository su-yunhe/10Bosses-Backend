from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", search_enterprise),
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
]
