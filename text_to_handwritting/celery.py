import os
from celery import Celery
import django
# Укажите название Django-проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'text_to_handwritting.settings')
django.setup()
app = Celery('text_to_handwritting')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в установленных приложениях
app.autodiscover_tasks()
