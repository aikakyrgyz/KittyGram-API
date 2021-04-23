from rest_framework import serializers
from rest_framework import serializers
from .models import Messages, User


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['sender_name', 'receiver_name', 'description', 'time']
        read_only_fields = ('sender_name', 'receiver_name', 'time')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender_name'] = instance.sender_name.email
        representation['receiver_name'] = instance.receiver_name.email
        return representation


class ViewSentMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['receiver_name', 'description', 'time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['receiver_name'] = instance.receiver_name.email
        return representation


class ViewReceivedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['sender_name', 'description', 'time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender_name'] = instance.sender_name.email
        return representation
