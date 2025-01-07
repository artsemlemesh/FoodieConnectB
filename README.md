



websockets
#pip install channels channels-redis

INSTALLED_APPS += [
    'channels',
]

ASGI_APPLICATION = 'your_project.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Ensure Redis is running
        },
    },
}

#install redis
   brew install redis

#start redis
   brew services start redis
   
   redis-server

   redis-cli ping

#after redis is running on the background it wont be in console


after fixing websokets install celery for ETA updates
#    pip install 'celery[redis]'


run worker in separate consoles######################################
# redis-server
# celery -A myproject worker --loglevel=info
# daphne -b 0.0.0.0 -p 8000 myproject.asgi:application



#pip freeze > requirements.txt

python manage.py populate_db 
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application
pip freeze > requirements.txt