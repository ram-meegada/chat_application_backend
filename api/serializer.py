from rest_framework import serializers
from .models import *

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'email', 'name']

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'name']

class MessagesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    class Meta:
        model = ChatStorageModel
        fields = ['id', 'name', 'userId', 'message', 'timestamp']
    def get_name(self, obj):
        try:
            return obj.user.name
        except:
            return ""
    def get_userId(self, obj):
        try:
            return obj.user.id
        except:
            return ""
    def get_timestamp(self, obj):
        try:
            return obj.created_at
        except:
            return ""
          
