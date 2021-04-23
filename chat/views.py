from django.contrib.auth import get_user_model
from django.shortcuts import render, HttpResponse, redirect
from rest_framework.generics import get_object_or_404

from .models import User, Messages
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from chat.serializers import MessageSerializer, ViewSentMessageSerializer, ViewReceivedMessageSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status


class SendMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def post(self, request, username=None):
        User = get_user_model()
        user = get_object_or_404(User, username=username)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender_name=request.user, receiver_name = user)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SentViewMessage(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]

    def get(self, request):
        user = self.request.user
        messages = Messages.objects.filter(sender_name=user)
        serializer = ViewSentMessageSerializer(messages, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response('You have not messaged anyone')


class ReceivedViewMessage(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def get(self, request):
        user = self.request.user
        messages = Messages.objects.filter(receiver_name=user)
        serializer = ViewReceivedMessageSerializer(messages, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response('You have no received messages')
