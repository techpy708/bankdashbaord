from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from dashboard.models import Observation

class Command(BaseCommand):
    help = "Send reminders for open & approved observations near/after due date"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        reminders_sent = 0

        qs = Observation.objects.filter(status="OPEN", approved="YES", due_date__isnull=False)

        for obs in qs:
            days_left = (obs.due_date - today).days

            if days_left in [5, 4, 3, 2, 1]:
                subject = f"Reminder: Observation due in {days_left} day(s)"
                message = (
                    f"Observation: {obs.observation}\n"
                    f"Due Date: {obs.due_date}\n"
                    f"Status: OPEN\n\n"
                    f"Please take necessary action before the due date."
                )
            elif days_left < 0:  # overdue
                subject = f"Overdue Alert: Observation due on {obs.due_date}"
                message = (
                    f"Observation: {obs.observation}\n"
                    f"Due Date: {obs.due_date} (Expired {abs(days_left)} day(s) ago)\n"
                    f"Status: OPEN\n\n"
                    f"This observation is overdue and requires immediate attention."
                )
            else:
                continue

            recipients = list(obs.email_recipients.values_list("email", flat=True))
            if not recipients:
                continue

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
            )
            reminders_sent += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Sent {reminders_sent} reminders"))
