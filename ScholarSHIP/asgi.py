"""
ASGI config for ScholarSHIP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ScholarSHIP.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import recruit.routing
import chat.routing

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'websocket': URLRouter(
        chat.routing.websocket_urlpatterns + recruit.routing.websocket_urlpatterns
    ),
})