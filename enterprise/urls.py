from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", enterprise_search),
    path("whoosh_search", whoosh_search),
    path("get_enterprise_recruitment", get_enterprise_recruitment),
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
]
