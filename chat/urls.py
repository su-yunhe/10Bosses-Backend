from django.urls import path

from .views import *

urlpatterns = [
    path("open_conversation", open_conversation),
    # path("send_message", send_message),
    path("get_conversations", get_conversations),
    path("get_history_messages", get_history_messages),
    # path("read_message", read_message)
]
