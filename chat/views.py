from django.shortcuts import render, HttpResponse, redirect
from .models import User, Messages
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from chat.serializers import MessageSerializer



# class SendMessage(generics.CreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
#
#     def post(self, request, reciever):
#         reciever = User.objects.get(username=reciever)
#         sender = request.user
#         serializer = MessageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(reciever=reciever, sender=sender)
#             return Response(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#

def getUserId(username):
    """
    Get the user id by the username
    :param username:
    :return: int
    """
    use = User.objects.get(username=username)
    id = use.id
    return id


def chat(request, username):
    """
    Get the chat between two users.
    :param request:
    :param username:
    :return:
    """

    friend = User.objects.get(username=username)
    id = getUserId(request.user.username)
    curr_user = User.objects.get(id=id)
    messages = Messages.objects.filter(sender_name=curr_user, receiver_name=friend) | Messages.objects.filter(sender_name=friend, receiver_name=curr_user)
    print(messages)
    if request.method == "GET":
        # return render(request, "chat/messages.html",
        #               {'messages': messages,
        #                'curr_user': curr_user, 'friend': friend})
        return JsonResponse(locals())



@csrf_exempt
def message_list(request, sender=None, receiver=None):
    if request.method == 'GET':
        messages = Messages.objects.filter(sender_name=sender, receiver_name=receiver, seen=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.seen = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
