from django.urls import path
from .views import *

urlpatterns = [
    path("trend_add", trend_add),
    path("get_person_single_trend", get_person_single_trend),
    path("get_peroson_all_trend", get_peroson_all_trend),
    path("delete_trend", delete_trend),
    path("like_trend", like_trend),
    path("comment_trend", comment_trend),
    path("get_trend_like_users", get_trend_like_users),
    path("get_trend_comments", get_trend_comments),
    path("delete_like", delete_like),
    path("transport_trend", transport_trend),
    path("upload_picture", upload_picture),
    path("get_enterprise_trends", get_enterprise_trends)
]
