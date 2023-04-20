from django import forms
from django.contrib.auth.forms import UserCreationForm
from psbackend.models import PSUsername
from .models import UserProfile, User

class UserForm(UserCreationForm):
    ps_username = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'ps_username')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        ps_username = PSUsername.objects.create(username=self.cleaned_data['ps_username'])
        UserProfile.objects.create(user=user, ps_username=ps_username)
        return user
