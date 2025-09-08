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

def fetch_rbi_notifications_job():
    url = "https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=RSS"
    feed = feedparser.parse(url)

    for entry in feed.entries[:10]:
        # Parse published date string to datetime object
        published_str = getattr(entry, 'published', None) or getattr(entry, 'updated', None)
        published_at = None
        if published_str:
            # feedparser returns struct_time; convert to datetime
            published_at = datetime(*entry.published_parsed[:6])
        
        # Check for duplicate by link
        if not Notification.objects.filter(link=entry.link).exists():
            Notification.objects.create(
                title=entry.title,
                link=entry.link,
                published_at=published_at,
                fetched_at=now()
            )
    print("✅ RBI Notifications synced")

