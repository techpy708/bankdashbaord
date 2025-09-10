# dashboard/jobs.py
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

def send_due_reminders_job():
    try:
        call_command("send_due_reminders")
        logger.info("✅ Due reminders sent successfully")
    except Exception as e:
        logger.error(f"❌ Error sending reminders: {e}")



# dashboard/jobs.py
import feedparser
from django.utils.timezone import now
from datetime import datetime
from django.utils.dateparse import parse_datetime
from dashboard.models import Notification  # adjust if different app name

# dashboard/jobs.py
import feedparser
from datetime import datetime, timedelta
from django.utils.timezone import now
from dashboard.models import Notification

# dashboard/jobs.py
import feedparser
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from dashboard.models import Notification

import feedparser
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from dashboard.models import Notification
import email.utils  # for parsing pubDate strings

def fetch_rbi_notifications_job():
    url = "https://rbi.org.in/notifications_rss.xml"
    feed = feedparser.parse(url)

    is_first_time = Notification.objects.count() == 0
    cutoff_date = now() - timedelta(days=180)  # last 6 months

    count = 0
    print(f"Feed entries fetched: {len(feed.entries)}")

    for entry in feed.entries:
        # Try to get published_at from published_parsed or pubDate
        published_at = None

        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "published") and entry.published:
            # parse the pubDate string e.g., "Fri, 05 Sep 2025 18:40:00"
            published_at = make_aware(datetime(*email.utils.parsedate(entry.published)[:6]))

        if not published_at:
            published_at = now()  # fallback

        # First run → last 6 months only
        if is_first_time and published_at < cutoff_date:
            continue

        obj, created = Notification.objects.get_or_create(
            link=entry.link,
            defaults={
                "title": entry.title,
                "message": getattr(entry, "summary", ""),
                "published_at": published_at,
            }
        )

        if created:
            print(f"✅ Added: {entry.title} ({published_at})")
            count += 1

    print(f"✅ RBI Notifications synced: {count} new notifications.")
    return count
