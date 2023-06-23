import logging
from celery import Celery
from config import Config
from kombu import Queue

logger = logging.getLogger(__name__)

app = Celery(
    broker=Config.rabbitmq_url,
    include=[
        'src.entrypoints.celery.tasks',
    ]
)

app.conf.task_queues = (
    Queue('events'),
)

app.conf.task_routes = {
    'src.entrypoints.celery.tasks.process_message_bus_event': {'queue': 'events'}
}
