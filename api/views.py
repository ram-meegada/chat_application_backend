from django.shortcuts import render
from .serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from .models import ChatSessionModel, ChatStorageModel
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import random
from chat_application.settings import EMAIL_HOST_USER 
from threading import Thread

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
                message = make_otp()
                user.otp = message
                user.save()
                Thread(target=send_otp_via_mail, args=(user.email, user.name, message)).start()
                return Response({"data": serializer.data, "message": "Login successfully", "status": 200}, status=200)
            else:
                return Response({"data": None, "message": "Invalid Password", "status": 400}, status=400)
        except UserModel.DoesNotExist:
            return Response({"data": None, "message": "User not found", "status": 400}, status=400)
        except Exception as err:
            return Response({"data": None, "message": "Something went wrong", "status": 400}, status=400)


def make_otp():
    otp = "".join(str(random.randint(0,9))for _ in range(4))
    return otp

def send_otp_via_mail(email, first_name, message):
    name = first_name
    context = {
        "OTP": message,
        "Name": name,
    }
    temp = render_to_string('otp.html', context)
    msg = EmailMultiAlternatives("No Reply!", temp, EMAIL_HOST_USER, [email])
    msg.content_subtype = 'html'
    msg.send()
    return message

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

class OtpVerificationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user = UserModel.objects.get(id=request.data["id"])
            if user.otp == request.data["otp"]:
                token = RefreshToken.for_user(user)
                return Response({"data": None, "access_token": str(token.access_token), "message": "", "status": 200}, status=200)
            return Response({"data": None, "message": "Wrong otp", "status": 400}, status=400)
        except Exception as err:
            return Response({"data": str(err), "message": "Something went wrong", "status": 400}, status=400)

class ResendOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user = UserModel.objects.get(id=request.data["id"])
            message = make_otp()
            user.otp = message
            user.save()
            Thread(target=send_otp_via_mail, args=(user.email, user.name, message)).start()
            return Response({"data": None, "message": "", "status": 200}, status=200)
        except Exception as err:
            return Response({"data": str(err), "message": "Something went wrong", "status": 400}, status=400)
