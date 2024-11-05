from django.db import models
from django.contrib.auth.models import AbstractBaseUser
# Create your models here.

class UserModel(AbstractBaseUser):
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=1000)
    name = models.CharField(max_length=100)
    otp = models.CharField(max_length=4, blank=True)
    otp_verification = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class ChatSessionModel(BaseModel):
    uuid = models.CharField(max_length=100, blank=True, null=True)
    user_one = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="client_user")
    user_two = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="talent_user")

    class Meta:
        db_table = "Chat Sessions"

class ChatStorageModel(BaseModel):
    session = models.ForeignKey(ChatSessionModel, on_delete=models.CASCADE)
    message = models.JSONField(default=dict)

    class Meta:
        db_table = "Chat Storage"
