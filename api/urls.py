from django.urls import path
from .views import *
from .consumers import *

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('users/', UsersListingView.as_view()),
    path('history/<int:id>/', MessagesListingView.as_view()),
]


websocket_urlpatterns = [
    path('chat/<int:user1>/<int:user2>/', ChattingConsumer.as_asgi())
]
