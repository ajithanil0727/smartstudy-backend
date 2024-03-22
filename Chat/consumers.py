from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import ChatRoom, Chat, UnreadMessage, UserStatus
from SmartUsers.models import CustomUser
from .serializers import ChatSerializer



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope.get("user")
        chat_with_id = self.scope.get("chat_with")
        
        if user_id is None or chat_with_id is None:
            await self.close()
            return

        # Assign user and chat_with
        self.user = await self.get_user(user_id)
        self.chat_with = await self.get_user(chat_with_id)
        
        if self.user is None or self.chat_with is None:
            await self.close()
            return

        # Generate room name based on user IDs
        self.room_name = f"chat_{min(self.user.id, self.chat_with.id)}_{max(self.user.id, self.chat_with.id)}"

        # Join room
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        # Update user online status
        await self.update_online_status(True)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        # Update user online status
        await self.update_online_status(False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        
        if message:
            # Save and send message immediately
            await self.save_and_send_message(message)
            
            # Check if the recipient is online
            is_recipient_online = await self.is_user_online(self.chat_with)

            if not is_recipient_online:
                await self.store_unread_message(message)

    async def save_and_send_message(self, message):
        # Save message to database
        room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)
        chat = await database_sync_to_async(Chat.objects.create)(content=message, user=self.user, room=room)

        # Serialize chat message
        serializer = ChatSerializer(chat)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': serializer.data
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    @database_sync_to_async
    def update_online_status(self, is_online):
        user_status, _ = UserStatus.objects.get_or_create(user=self.user)
        user_status.is_online = is_online
        user_status.save()

    @database_sync_to_async
    def is_user_online(self, user):
        user_status, _ = UserStatus.objects.get_or_create(user=user)
        return user_status.is_online

    @database_sync_to_async
    def store_unread_message(self, message):
        UnreadMessage.objects.create(receiverby=self.chat_with, message=message, sentby=self.user)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope.get("user")
        if user_id is None:
            await self.close()
            return
        user_channel_name = f"user_{user_id}"
        await self.channel_layer.group_add(user_channel_name, self.channel_name)

        # Update user online status
        await self.update_online_status(True)

        await self.accept()

        # Fetch all unread messages for the user
        unread_messages = await self.get_unread_messages(user_id)
        # Send unread messages to the user
        
        await self.send_notification(unread_messages)


        

    async def disconnect(self, close_code):
        user_id = self.scope.get("user")
        if user_id is None:
            return
        user_channel_name = f"user_{user_id}"
        await self.channel_layer.group_discard(user_channel_name, self.channel_name)

        # Update user online status
        await self.update_online_status(False)

    async def send_notification(self, message):
        await self.send(text_data=json.dumps(message))


    async def get_unread_messages(self, user):
        print("code entered this function")
        # Execute the database operation asynchronously
        unread_messages = await database_sync_to_async(
            lambda: list(UnreadMessage.objects.filter(receiverby=user).values('sentby', 'message'))
        )()
        print(unread_messages)
        return unread_messages

    async def update_online_status(self, is_online):
        print("code entered this function2")
        user_id = self.scope.get('user')
        user = await database_sync_to_async(CustomUser.objects.get)(pk=user_id)
        user_status, _ = await database_sync_to_async(UserStatus.objects.get_or_create)(user=user)
        user_status.is_online = is_online
        await database_sync_to_async(user_status.save)()

    # @database_sync_to_async
    # def get_unread_messages(self, user):
    #     print("code entyered this function")
    #     return UnreadMessage.objects.filter(user=user).values('user', 'message')

    # @database_sync_to_async
    # def update_online_status(self, is_online):
    #     print("code entered this function2")
    #     user_status, _ = UserStatus.objects.get_or_create(user=self.scope['user'])
    #     user_status.is_online = is_online
    #     user_status.save()

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         user_id = self.scope['user'].id
#         user_channel_name = f"user_{user_id}"
#         await self.channel_layer.group_add(user_channel_name, self.channel_name)

#         # Update user online status
#         await self.update_online_status(True)

#         await self.accept()

#     async def disconnect(self, close_code):
#         user_id = self.scope['user'].id
#         user_channel_name = f"user_{user_id}"
#         await self.channel_layer.group_discard(user_channel_name, self.channel_name)

#         # Update user online status
#         await self.update_online_status(False)

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps(event))

#     @database_sync_to_async
#     def update_online_status(self, is_online):
#         user_status, _ = UserStatus.objects.get_or_create(user=self.scope['user'])
#         user_status.is_online = is_online
#         user_status.save()


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         request_user = self.scope['user']
#         chat_with_user = self.scope['chat_with']
#         user_ids = [str(request_user), str(chat_with_user)]
#         user_ids = sorted(user_ids)
#         self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()


#     async def disconnect(self, close_code):
#         self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )


#     async def receive(self, text_data=None, byte_data=None):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         room = await database_sync_to_async(ChatRoom.objects.get)(name = self.room_group_name)
#         chat = Chat(
#             content=message,
#             user=await database_sync_to_async(CustomUser.objects.get)(id = self.scope['user']),
#             room=room
#         )
#         await database_sync_to_async(chat.save)()
#         data = ChatSerializer(chat)
#         await  self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': data.data
#             }
#         )
#         await send_notification_to_user(f'notifications_{str(self.scope["chat_with"])}','You have a message',str(self.scope['user']))
#     async def chat_message(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps(message))


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Retrieve user and chat_with from scope
#         user_id = self.scope.get("user")
#         chat_with_id = self.scope.get("chat_with")
        
#         if user_id is None or chat_with_id is None:
#             await self.close()
#             return

#         # Assign user and chat_with
#         self.user = await self.get_user(user_id)
#         self.chat_with = await self.get_user(chat_with_id)
        
#         if self.user is None or self.chat_with is None:
#             await self.close()
#             return

#         # Generate room name based on user IDs
#         room_name = f"chat_{min(self.user.id, self.chat_with.id)}_{max(self.user.id, self.chat_with.id)}"

#         # Join room
#         await self.channel_layer.group_add(room_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room
#         room_name = f"chat_{min(self.user.id, self.chat_with.id)}_{max(self.user.id, self.chat_with.id)}"
#         await self.channel_layer.group_discard(room_name, self.channel_name)

#     async def receive(self, text_data):
#         # Parse incoming message
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message')

#         if message:
#             # Save message to database
#             room_name = f"chat_{min(self.user.id, self.chat_with.id)}_{max(self.user.id, self.chat_with.id)}"
#             room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=room_name)
#             chat = await database_sync_to_async(Chat.objects.create)(content=message, user=self.user, room=room)

#             # Serialize chat message
#             serializer = ChatSerializer(chat)

#             # Send message to room group
#             await self.channel_layer.group_send(
#                 room_name,
#                 {
#                     'type': 'chat_message',
#                     'message': serializer.data
#                 }
#             )

#     async def chat_message(self, event):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps(event['message']))

#     async def get_user(self, user_id):
#         try:
#             return await database_sync_to_async(CustomUser.objects.get)(id=user_id)
#         except CustomUser.DoesNotExist:
#             return None