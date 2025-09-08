import datetime
import time
import feedparser

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now

from dashboard.models import Notification

class Command(BaseCommand):
    help = "Fetch latest RBI notifications from RSS feed and save to DB"

    def handle(self, *args, **options):
        url = "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=RSS"
        feed = feedparser.parse(url)

        count = 0

        for entry in feed.entries[:10]:
            # Avoid duplicates by link
            if not Notification.objects.filter(link=entry.link).exists():
                # Convert published time to datetime object
                published_parsed = entry.published_parsed  # time.struct_time
                published_dt = datetime.datetime.fromtimestamp(time.mktime(published_parsed))
                published_dt_aware = make_aware(published_dt)

                Notification.objects.create(
                    title=entry.title,
                    link=entry.link,
                    published_at=published_dt_aware,
                    fetched_at=now()
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ RBI Notifications synced: {count} new notifications."))
