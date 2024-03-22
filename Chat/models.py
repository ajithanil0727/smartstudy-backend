import uuid
from django.db import models
from SmartUsers.models import CustomUser 




class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=1000,default='message')
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

class UserStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)

class UnreadMessage(models.Model):
    receiverby = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    sentby = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)