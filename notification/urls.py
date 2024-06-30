from django.urls import path

from .views import *

urlpatterns = [
    path("employee_quit_notification", employee_quit_notification),
    path("resume_notification", resume_notification),
    path("user_reply_notification", user_reply_notification),
    path("get_notification_list", get_notification_list),
    path("get_notification_list1", get_notification_list1),
    path("get_notification_list2", get_notification_list2),
    path("get_notification_list3", get_notification_list3),
    path("get_notification_detail", get_notification_detail),
    path("delete_notification", delete_notification),
]