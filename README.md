# Plemiona API

## Requirements

- Python 3.9+
- Redis

## Setting Up Development Environment

Get redis: (https://redis.io/topics/quickstart)
```bash
sudo apt install redis-server
```

Run redis service:
```bash
sudo service redis-server start
# or
sudo systemctl start redis-server.service
```

Clone repo:
```bash
git clone git@github.com:MendelDamian/plemiona-engine.git
cd plemiona-engine
```

Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install packages:
```bash
pip install -r requirements.txt
```

Apply migrations:
```bash
python manage.py migrate
```

Start Celery worker process:
```bash
celery -A plemiona_api worker -l info
```

Run development server:
```bash
python manage.py runserver
```
