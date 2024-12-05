



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
