import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from Chat.channelMiddleware import JWTwebsocketMiddleware
from Chat.routes import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartStudy.settings')
django.setup()
application = get_asgi_application()
application = ProtocolTypeRouter({
    'http':application,
    'websocket':JWTwebsocketMiddleware(URLRouter(websocket_urlpatterns))
})
