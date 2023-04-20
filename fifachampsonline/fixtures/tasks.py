from celery import shared_task
from django.core.management import call_command

@shared_task
def send_reminder_emails():
    call_command('send_reminder_emails')