from channels.middleware import BaseMiddleware
from django.db import close_old_connections
import jwt
from django.conf import settings


class JWTwebsocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        print(scope)
        query_string = scope.get('query_string', b"").decode('utf-8','replace')
        print(query_string)
        try:
            query_params = dict(qp.split('=') for qp in query_string.split('&'))
        except:
            query_params = dict(query_string.split("="))
        token = query_params.get('token', None)
        receiver_id = query_params.get('chat_with', None)
        if token is None:
            await send({
                'type': 'websocket.close',
                'code': 4000
            })
        else:
            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
                user_id = decoded_token['user_id']
                if user_id:
                    scope['user'] = user_id
                    if receiver_id:
                        scope['chat_with'] = receiver_id
                else:
                    await send({
                        'type': 'websocket.close',
                        'code': 4000
                    })
                return await super().__call__(scope, receive, send)
            except jwt.ExpiredSignatureError:
                await send({
                    'type': 'websocket.close',
                    'code': 4401  # Custom code for expired token
                })
            except jwt.InvalidTokenError:
                await send({
                    'type': 'websocket.close',
                    'code': 4400  # Custom code for invalid token
                })
            except Exception as e:
                print(e)
                