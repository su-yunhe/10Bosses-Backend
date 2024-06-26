from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", enterprise_search),
    path("whoosh_search", whoosh_search),
    path("get_enterprise_recruitment", get_enterprise_recruitment),
    path("recommend_enterprise", recommend_enterprise),
    path("update_enterprise", update_enterprise),
    path("show_enterprise", show_enterprise),
    path("delete_enterprise", delete_enterprise),
    path("show_enterprise_member", show_enterprise_member),
    path("show_recruitment_list", show_recruitment_list)  # 展示企业招聘列表
    # path("add_enterprise_member", add_enterprise_member),
]
