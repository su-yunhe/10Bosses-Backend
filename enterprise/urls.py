from django.urls import path

from .views import *

urlpatterns = [
    path("create_enterprise", create_enterprise),
    path("enterprise_search", search_enterprise),
    path("get_enterprise_recruitment", get_enterprise_recruitment),
    path("get_intended_recruitment", get_intended_recruitment),
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
    path("delete_enterprise", delete_enterprise),
    path("show_enterprise_member", show_enterprise_member),
    # path("add_enterprise_member", add_enterprise_member),
]
