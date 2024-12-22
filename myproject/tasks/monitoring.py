import cronitor
from django.conf import settings
from celery import shared_task
import logging
from django.db import connection
import redis

# Set up logging
logger = logging.getLogger(__name__)


cronitor.api_key = settings.CRONITOR_API_KEY

monitor = cronitor.Monitor('{}-CELERY-MONITOR'.format(settings.ENVIRONMENT))
# logger.info('monitor', monitor)

@shared_task(name='heat_beat_scheduler')
def send_heart_beat():
    logger.info("Sending heartbeat...")
    try:
        monitor.ping(message="Alive!")
        monitor.ping(metrics={'count': 100, 'error_count': 3})
        logger.info("Heartbeat sent successfully.")
    except Exception as e:
        logger.error(f"Error sending heartbeat: {e}")





@shared_task(name='check_health')
def check_health():
    health_status = {}
    
    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['database'] = 'Healthy'
    except Exception as e:
        health_status['database'] = f'Error: {str(e)}'
    
    # Check Redis connectivity
    try:
        redis_client = redis.StrictRedis(host='redis', port=6379)
        redis_client.ping()
        health_status['redis'] = 'Healthy'
    except Exception as e:
        health_status['redis'] = f'Error: {str(e)}'
    
    # Log health status
    logger.info(f"Task: check_health completed | Health Status: {health_status}")
    return health_status