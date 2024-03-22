from django.urls import path
from .views import *

urlpatterns = [
    path('', Notifications.as_view()),
    path('status/<str:id>', NotificationStatusChange.as_view()),
]