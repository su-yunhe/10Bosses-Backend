from django.urls import path

from .views import *

urlpatterns = [
    path("send_message", send_message),
    path("get_conversations", get_conversations),
]
