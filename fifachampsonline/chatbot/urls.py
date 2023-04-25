from django.urls import path, include

app_name = 'chatbot'

urlpatterns = [
    path('chatbot/', include('chatbot.urls')),
]
