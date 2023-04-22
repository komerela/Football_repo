from django.urls import path, include
from .views import MyRegisterView, MyLoginView, MyLogoutView, UserRetrieveView, UserDetailView, UserProfileDetailView

app_name = 'accounts'

urlpatterns = [
    path('register/', MyRegisterView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('user/<int:pk>/', UserRetrieveView.as_view(), name='user-detail'),
    path('user_api/<int:pk>/', UserDetailView.as_view(), name='user-detail-api'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),
]