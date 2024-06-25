from django.urls import path

from .views import *

urlpatterns = [
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
]
