from django.conf import settings
from django.shortcuts import render
from .openai_chatbot import OpenAIChatbot

class ChatbotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.chatbot = OpenAIChatbot(api_key=settings.OPENAI_API_KEY)

    def __call__(self, request):
        response = self.get_response(request)
        chatbot_html = render(request, 'chatbot.html').content
        response.content = response.content.replace(b'</body>', chatbot_html+b'</body>')
        return response
