# browse/urls.py
from django.urls import path

from . import views

urlpatterns = [
   path('welcome', views.welcome, name='welcome'),
   path('menu', views.menu, name='menu'),
   path('browse-content', views.browse_content, name='browse-content'),
   path('listen', views.listen, name='listen'),
   path('browse-requests', views.browse_requests, name='browse-requests'),
   path('request-content', views.request_content, name='request-content'),
]
