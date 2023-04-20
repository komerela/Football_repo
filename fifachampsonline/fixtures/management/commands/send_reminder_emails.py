from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from fixtures.models import Booking

class Command(BaseCommand):
    help = 'Sends reminders to users who have booked an event but not paid'

    def handle(self, *args, **options):
        # Get all unpaid bookings that are 12 hours away from the event
        twelve_hours_ago = timezone.now() - timezone.timedelta(hours=12)
        twelve_hours_later = timezone.now() + timezone.timedelta(hours=12)
        unpaid_bookings = Booking.objects.filter(
            paid=False,
            fixture__date_time__gte=twelve_hours_ago,
            fixture__date_time__lte=twelve_hours_later,
        )

        # Send reminder emails
        for booking in unpaid_bookings:
            subject = f"Reminder: Payment for {booking.fixture} is due soon"
            message = f"Dear {booking.user.username},\n\nThis is a friendly reminder that payment for your booking for {booking.fixture} is due soon. Please log in to your account and complete the payment process.\n\nThank you!"
            send_mail(
                subject,
                message,
                'noreply@myapp.com',
                [booking.user.email],
                fail_silently=False,
            )
