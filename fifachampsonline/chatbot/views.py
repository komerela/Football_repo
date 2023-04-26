import os
import sys

from django.shortcuts import render
from .models import ChatbotResponse
from chatbot.openai_chatbot import OpenAIChatbot

def chatbot(request):
    chatbot = OpenAIChatbot(api_key=os.getenv("OPENAI_API_KEY"))
    if request.method == 'POST':
        message = request.POST.get('message', '')
        response = chatbot.generate_response(message=message)
        if "I'm sorry, I don't understand the question." in response:
            suggested_responses = ['Can you please rephrase your question?', 'Can you provide more information?', 'Would you like to speak to a human representative?']
            return render(request, 'base.html', {'message': response, 'suggested_responses': suggested_responses})
        else:
            ChatbotResponse.objects.create(input=message, output=response)
            return render(request, 'base.html', {'message': response})
        
    responses = ChatbotResponse.objects.all()
    return render(request, 'base.html', {'responses': responses})


"""
This modified view function retrieves the 10 most recent chatbot responses from the 
database and passes them to the chatbot.html template.
ChatbotView that inherits from Django's View class. We create an instance of OpenAIChatbot 
inside the __init__ method, and pass in our API key. We've defined get and post methods for 
handling GET and POST requests, respectively. In the get method, we retrieve the 10 most recent 
chatbot responses from the database and pass them to the chatbot.html template. In the post method, 
we get the user's message from the POST request, generate a response using self.chatbot, and return 
a JsonResponse object containing the chatbot's response. If the chatbot's response indicates that it 
didn't understand the question, we include a list of suggested responses in the JSON data.
Note that we've used self.chatbot to refer to the OpenAIChatbot instance inside the class methods. 
This is because chatbot is an instance variable of the ChatbotView class, and can be accessed from any method using self.chatbot.
"""
