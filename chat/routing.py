
from django.urls import re_path

from chat import consumers


websocket_urlpatterns = [
    re_path(r'ws/message/(?P<conversation_id>\d+)/$', consumers.ChatConsumer),
]
