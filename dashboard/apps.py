from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
import logging

logger = logging.getLogger(__name__)

class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):

        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from dashboard.jobs import send_due_reminders_job, fetch_rbi_notifications_job  # <-- Import here

        scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Run every day at 11:00 AM
        scheduler.add_job(
            send_due_reminders_job,
            trigger="cron",
            hour=11,
            minute=0,
            id="send_due_reminders",
            replace_existing=True,
        )

        scheduler.add_job(
            fetch_rbi_notifications_job,
            trigger="cron",
            hour=17,   # Run every morning at 9:00 AM
            minute=36,
            id="fetch_rbi_notifications",
            replace_existing=True,
        )

        try:
            scheduler.start()
        except Exception as e:
            logger.error(f"Scheduler failed to start: {e}")
        
        from django.contrib.auth import get_user_model
        from .models import Department

        User = get_user_model()
        try:
            if not User.objects.filter(username='admin').exists():
                user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='password123@@',
                    branch_code='B001',
                    
                    user_role = 'Admin'
                )
                user.departments.set(Department.objects.all())
                print("✅ Default admin user created.")
        except (OperationalError, ProgrammingError):
            # This avoids issues before migrations are applied
            pass
