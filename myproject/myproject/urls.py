"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from myproject import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from webhooks.sentry_webhook import sentry_error_webhook


urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include('users.urls', namespace='users')),#'users:login' #namespace is the same as # app_name= 'users', if there are the same names of urls in different apps then it wont be confused
    path('cart/', include('cart.urls', namespace='cart')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('api/sentry-error/', sentry_error_webhook, name='sentry-error-webhook'),

]

if settings.DEBUG: # setting the address to display uploaded picture on the page
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Serve static files

