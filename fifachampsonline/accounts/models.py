from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)

class User(models.Model):
    # your model fields here

    @classmethod
    def authenticate_user(cls, username, password):
        # create a new user
        user = User.objects.create_user(username=username, email='', password=password)

        # authenticate the user
        user = authenticate(username=username, password=password)

        # check if user is authenticated
        if user is not None:
            # user is authenticated
            return user
        else:
            # user is not authenticated
            return redirect('login')


