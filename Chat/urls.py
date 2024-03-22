from django.urls import path
from .views import *

urlpatterns = [
    path('chathistory/<int:id>/', Chats.as_view()),
    path('deleteUnread/<int:user_id>/', DeleteUnread , name='deleteunread')
]