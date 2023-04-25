from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import UserProfile
from django.views.generic import RedirectView


class UserProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserProfile
    template_name = 'user_detail.html'
    context_object_name = 'user'

    def test_func(self):
        user = self.get_object()
        return user == self.request.user


# if self.request.user == self.get_object().user: 
# similar to this
# user = self.get_object()
# return user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        if user == self.request.user:
            context['show_ps_username'] = True
        else:
            context['show_ps_username'] = False
        return context
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect('home')

class MyRegisterView(CreateView):
    form_class = UserForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     login(self.request, self.object)
    #     messages.success(self.request, "You have successfully registered!")
    #     return response
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        success_message = "You have successfully registered!"
        messages.success(self.request, success_message)
        return response

class MyLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "You have successfully logged in!")
        return response

class MyLogoutView(RedirectView):
    url = reverse_lazy('logout')
    template_name = 'logout.html'

class UserRetrieveView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class UserDetailView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist, Register User to continue")
        
        # Return the user data if it exists
        serializer = UserSerializer(user)
        return Response(serializer.data)
