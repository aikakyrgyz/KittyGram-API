from django.urls import path, include
from .views import SendMessage, SentViewMessage, ReceivedViewMessage

urlpatterns = [
    path("message/<slug:username>/", SendMessage.as_view(), name="chat"),
    path('view-messages-sent/', SentViewMessage.as_view()),
    path('view-messages-received/', ReceivedViewMessage.as_view())
]