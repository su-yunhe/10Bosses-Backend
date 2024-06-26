from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", search_enterprise),
    path("get_enterprise_recruitment", get_enterprise_recruitment),
    path("get_intended_recruitment", get_intended_recruitment),
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
]
