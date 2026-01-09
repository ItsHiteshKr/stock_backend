from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL (default local Redis)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery instance
celery_app = Celery(
    "stock_backend",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_tasks"]  # Import tasks module
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Har 5 minute me selected stocks ka intraday data fetch kare
    "fetch-intraday-data-every-5-minutes": {
        "task": "celery_tasks.fetch_all_stocks_intraday",
        "schedule": crontab(minute="*/5"),  # Har 5 minute
    },
    # Market hours me har minute data fetch kare (9:15 AM - 3:30 PM IST)
    "fetch-intraday-data-market-hours": {
        "task": "celery_tasks.fetch_all_stocks_intraday",
        "schedule": crontab(
            minute="*",
            hour="9-15",  # 9 AM to 3 PM
            day_of_week="mon-fri"  # Monday to Friday
        ),
    },
}
