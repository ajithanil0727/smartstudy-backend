from django.http import JsonResponse
from django.shortcuts import render
from SmartUsers.models import CustomUser
from .models import UnreadMessage
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import settings
import jwt
from .serializers import ChatSerializer
# from SmartUsers.models import ChatUsersSerializers
# from notification.models import NotificationRoom, Notification
from .models import Chat, ChatRoom


class Chats(APIView):
    def get(self, request, id):
        access_token = request.GET.get('token', '')  # Get the access token from the query parameter
        if not access_token:
            return Response("Access token is missing in the request.", status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})['user_id']
        except Exception as e:
            print(e)
            return Response("Invalid access token.", status=status.HTTP_401_UNAUTHORIZED)

        user_ids = sorted([str(user_id), str(id)])
        room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        
        room, _ = ChatRoom.objects.get_or_create(name=room_group_name)
        chats = Chat.objects.filter(room=room).order_by('timestamp')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

def DeleteUnread(request, user_id):
    user_messages = UnreadMessage.objects.filter(receiverby=user_id)
    
    if user_messages.exists():
        user_messages.delete()
        return JsonResponse({'success': True, 'message': 'Unread messages deleted successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'No unread messages found for the user.'})


# class ChatLists(APIView):
#     def get(self, request, id):
#         chatroom = ChatRoom.objects.filter(name__contains=str(id))
#         users = []
#         if chatroom:
#             for room in chatroom:
#                 ids = room.name.split('_')
#                 ids.pop(0)
#                 ids = [i for i in ids if i != str(id)]
#                 print('ids', ids)
#                 if ids:
#                     users.append(CustomUser.objects.get(id=ids[0]))
#             if users:
#                 users_serializer = ChatUsersSerializers(users, many=True)
#                 return Response(users_serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response([], status=status.HTTP_200_OK)
#         return Response(users, status=status.HTTP_200_OK)

