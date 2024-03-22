"""
ASGI config for SmartStudy project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from Chat.channelMiddleware import JWTwebsocketMiddleware
from Chat.routes import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartStudy.settings')

application = get_asgi_application()
application = ProtocolTypeRouter({
    'http':application,
    'websocket':JWTwebsocketMiddleware(URLRouter(websocket_urlpatterns))
})
