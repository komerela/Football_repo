from django.contrib import admin
from .models import ChatbotResponse

@admin.register(ChatbotResponse)
class ChatbotResponseAdmin(admin.ModelAdmin):
    list_display = ('input', 'output', 'created_at')
    search_fields = ('input', 'output')
    list_filter = ('created_at',)