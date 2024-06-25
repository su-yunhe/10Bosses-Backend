from django.urls import path

from .views import *

urlpatterns = [
    path("publish_recruitment", publish_recruitment),  # 发布招聘信息
    path("show_recruitment", publish_recruitment),  # 修改招聘信息
    path("update_recruitmrnt", update_recruitmrnt),  # 修改招聘信息
    path("show_material", show_material),  # 查看申请列表
    path("show_material_single", show_material_single)  # 查看申请列表
]
