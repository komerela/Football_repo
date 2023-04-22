import openai
from .models import ChatbotResponse

# generate_response() function to handle cases where the chatbot doesn't understand the question

class OpenAIChatbot:
    def __init__(self, api_key):
        openai.api_key = api_key
        
    def generate_response(self, message):
        response = openai.Completion.create(
            engine="davinci",
            prompt=message,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text = response.choices[0].text.strip()
        if response_text == "":
            response_text = "I'm sorry, I don't understand the question. Can you please rephrase or provide more information?"
        ChatbotResponse.objects.create(input=message, output=response_text)
        return response_text
