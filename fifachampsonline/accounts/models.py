from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from psbackend.models import PSUsername

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_points = models.IntegerField(default=0)
    ps_username = models.ForeignKey(PSUsername, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username}'s profile"

class MyUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)
    ps_username = models.ForeignKey(PSUsername, on_delete=models.CASCADE)

    @classmethod
    def authenticate_user(cls, email, password):
        # authenticate the user
        user = authenticate(email=email, password=password)

        # check if user is authenticated
        if user is not None:
            # user is authenticated
            return user
        else:
            # user is not authenticated
            return redirect('login')
