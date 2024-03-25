from rest_framework import serializers
from .models import Chat, ChatRoom, UnreadMessage
from SmartUsers.serializers import CustomUserSerializer 



class ChatSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Chat
        fields = ['content', 'timestamp', 'user']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class UnreadMessageSerializer(serializers.ModelSerializer):
    receiverby = CustomUserSerializer()
    sentby = CustomUserSerializer()

    class Meta:
        model = UnreadMessage
        fields = ('id', 'receiverby', 'sentby', 'message', 'timestamp')