# Celery Worker & Beat Commands

## Prerequisites
```bash
# Redis install kare (Windows ke liye)
# Download from: https://github.com/microsoftarchive/redis/releases
# Or Docker se run kare:
docker run -d -p 6379:6379 redis

# Dependencies install kare
pip install -r requirements.txt
```

## Run Celery Worker
```bash
# Worker start kare (separate terminal me)
celery -A celery_config worker --loglevel=info --pool=solo
```

## Run Celery Beat (Scheduler)
```bash
# Beat scheduler start kare (separate terminal me)
celery -A celery_config beat --loglevel=info
```

## Run Flower (Celery Monitoring Tool)
```bash
# Flower start kare (optional - monitoring ke liye)
celery -A celery_config flower --port=5555
# Browser me kholen: http://localhost:5555
```

## Run All Together (Development)
```bash
# Terminal 1: Redis (if not using Docker)
redis-server

# Terminal 2: Celery Worker
celery -A celery_config worker --loglevel=info --pool=solo

# Terminal 3: Celery Beat
celery -A celery_config beat --loglevel=info

# Terminal 4: FastAPI Server
uvicorn main:app --reload

# Terminal 5 (Optional): Flower
celery -A celery_config flower
```

## Manual Task Trigger (Python me)
```python
from celery_tasks import fetch_intraday_data, fetch_all_stocks_intraday

# Single stock ke liye
result = fetch_intraday_data.delay("RELIANCE.NS")
print(result.id)  # Task ID

# All stocks ke liye
result = fetch_all_stocks_intraday.delay()
print(result.id)

# Selected stocks ke liye
from celery_tasks import fetch_selected_stocks_intraday
result = fetch_selected_stocks_intraday.delay(["RELIANCE.NS", "TCS.NS", "INFY.NS"])
```

## Environment Variables (.env file me add kare)
```
REDIS_URL=redis://localhost:6379/0
```

## Production Deployment
```bash
# Supervisor ya systemd use kare production me
# Example supervisor config:

[program:celery_worker]
command=/path/to/venv/bin/celery -A celery_config worker --loglevel=info
directory=/path/to/stock_backend
user=your_user
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A celery_config beat --loglevel=info
directory=/path/to/stock_backend
user=your_user
autostart=true
autorestart=true
```

## Scheduled Tasks (Auto-configured)

1. **Market Hours Task**: Har minute data fetch kare (Monday-Friday, 9 AM - 3 PM IST)
2. **Every 5 Minutes**: Har 5 minute me data fetch kare (backup schedule)

Schedule customize karne ke liye `celery_config.py` me `beat_schedule` edit kare.
