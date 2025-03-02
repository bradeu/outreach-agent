import os
from celery import Celery
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
_ = load_dotenv(dotenv_path=env_path)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'app',
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,  # Process tasks one at a time
    task_acks_late=True,  # Acknowledge tasks after they are executed
    task_track_started=True,  # Track when tasks are started
    task_time_limit=3600,  # 1 hour time limit per task
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
)

celery_app.conf.task_routes = {
    'app.tasks.upsert_batch': {'queue': 'pinecone'},
}

if __name__ == '__main__':
    celery_app.start() 