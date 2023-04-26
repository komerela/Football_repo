from django.conf import settings
from django.shortcuts import render
from .openai_chatbot import OpenAIChatbot
from chatbot.models import ChatbotResponse

class ChatbotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.chatbot = OpenAIChatbot(api_key=settings.OPENAI_API_KEY)

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/chatbot'):
            responses = ChatbotResponse.objects.all().order_by('-created_at')[:10]
            chatbot_html = render(request, 'chatbot.html', {'responses': responses}).content
            response.content = response.content.replace(b'</body>', chatbot_html+b'</body>')
        return response

