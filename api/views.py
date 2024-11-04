from django.shortcuts import render
from .serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from .models import ChatSessionModel, ChatStorageModel
from django.db.models import Q

class SignUpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(password=make_password(request.data["password"]))
                return Response({"data": None, "message": "Sign up completed successfully", "status": 201}, status=201)
            return Response({"data": serializer.errors, "message": "Something went wrong", "status": 400}, status=400)
        except Exception as err:
            return Response({"data": None, "message": "Something went wrong", "status": 400}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user = UserModel.objects.get(email=request.data['email'])
            password_verification = check_password(request.data['password'], user.password)
            if password_verification:
                serializer = SignUpSerializer(user)
                token = RefreshToken.for_user(user)
                return Response({"data": serializer.data, "access_token": str(token.access_token), "message": "Login successfully", "status": 200}, status=200)
            else:        
                return Response({"data": None, "message": "Invalid Password", "status": 400}, status=400)
        except UserModel.DoesNotExist:
            return Response({"data": None, "message": "User not found", "status": 400}, status=400)
        except Exception as err:
            return Response({"data": None, "message": "Something went wrong", "status": 400}, status=400)

class UsersListingView(APIView):
    def get(self, request):
        try:
            user = UserModel.objects.exclude(id=request.user.id)
            serializer = UsersSerializer(user, many=True)
            return Response({"data": serializer.data, "message": "", "status": 200}, status=200)
        except Exception as err:
            return Response({"data": str(err), "message": "Something went wrong", "status": 400}, status=400)

class MessagesListingView(APIView):
    def get(self, request, id):
        try:
            session = ChatSessionModel.objects.get(Q(user_one=request.user, user_two=id) | Q(user_one=id, user_two=request.user))
            chats = ChatStorageModel.objects.filter(session=session).values()
            # serializer = MessagesSerializer(chats, many=True)
            return Response({"data": chats, "message": "", "status": 200}, status=200)
        except Exception as err:
            return Response({"data": str(err), "message": "Something went wrong", "status": 400}, status=400)
