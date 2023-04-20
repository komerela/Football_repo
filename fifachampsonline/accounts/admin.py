from django.contrib import admin
from .models import MyUser, PSUsername, UserProfile

# Register your models here.

admin.site.register(MyUser)
admin.site.register(PSUsername)
admin.site.register(UserProfile)


