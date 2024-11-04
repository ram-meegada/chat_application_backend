import json
from datetime import datetime
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from .models import ChatSessionModel, ChatStorageModel, UserModel
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken
import string
import random

def generate_session_id():
    chars = string.ascii_letters + string.digits
    alpha_numeric = ''.join([random.choice(chars) for _ in range(10)])
    return alpha_numeric

class ChattingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user1 = self.scope['url_route']['kwargs']['user1']
        self.user2 = self.scope['url_route']['kwargs']['user2']
        self.session = await database_sync_to_async(self.create_or_get_session)(self.user1, self.user2)
        await self.channel_layer.group_add(self.session.uuid, self.channel_name)
        await self.accept()
        print("--------connection established------------")

    def create_or_get_session(self, user1, user2):
        new_session_id = generate_session_id()
        get_user1 = UserModel.objects.get(id=user1)
        get_user2 = UserModel.objects.get(id=user2)
        self.user_name = get_user1.name
        try:
            session = ChatSessionModel.objects.get(Q(user_one_id=user1, user_two_id=user2) |
                                                   Q(user_one_id=user2, user_two_id=user1))
        except ChatSessionModel.DoesNotExist:
            session = ChatSessionModel.objects.create(uuid=new_session_id, user_one_id=get_user1.id, 
                                                          user_two_id=get_user2.id)
        return session

    async def receive(self, text_data):
        new_message_data = json.loads(text_data)
        # message_text = new_message_data["message"]
        timestamp = datetime.now().isoformat()

        # Save the message to the database
        saved_message = await database_sync_to_async(ChatStorageModel.objects.create)(
            session_id=self.session.id, 
            message = new_message_data
        )

        # Create the response message format
        # response_message = {
        #     "id": self.user1,
        #     "name": self.user_name,
        #     "message": message_text,
        #     "timestamp": timestamp
        # }

        await self.channel_layer.group_send(
            self.session.uuid,
            {
                'type': 'chat_message',
                'msg': json.dumps(new_message_data)  # Send the formatted response message
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=event["msg"])

    async def disconnect(self, close_code):
        print('websocket disconnected.....', close_code)
