import datetime
import time
import feedparser


# dashboard/management/commands/fetch_rbi_notifications.py
from django.core.management.base import BaseCommand
from dashboard.jobs import fetch_rbi_notifications_job

class Command(BaseCommand):
    help = "Fetch RBI notifications from RSS feed"

    def handle(self, *args, **options):
        count = fetch_rbi_notifications_job()
        self.stdout.write(self.style.SUCCESS(
            f"✅ RBI Notifications synced: {count} new notifications."
        ))
