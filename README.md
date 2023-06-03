# Plemiona API

## Instruction
```bash
# Clone repo
git clone git@github.com:MendelDamian/plemiona-engine.git
cd plemiona-engine

# Install Redis server
sudo apt-get install redis-server

# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Migrate
python manage.py migrate

# Start Redis server
sudo service redis-server start

# Start Celery worker process
celery -A plemiona_api worker -l info

# Run development server
python manage.py runserver
```
