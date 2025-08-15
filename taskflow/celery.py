# taskflow/celery.py
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings.base')

app = Celery('taskflow')

# Загружаем конфигурацию из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находить задачи в приложениях
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')