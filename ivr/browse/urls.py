# browse/urls.py
from django.urls import path

# from . import old_views
from browse.views.main import welcome
from browse.views.browse_content import browse_content
from browse.views.browse_requests import browse_requests
from browse.views.listen import listen
from browse.views.request import request_content

urlpatterns = [
   path('welcome', welcome, name='welcome'),
   # path('menu', views.menu, name='menu'),
   path('browse-content', browse_content, name='browse-content'),
   path('listen', listen, name='listen'),
   path('browse-requests', browse_requests, name='browse-requests'),
   path('request-content', request_content, name='request-content'),
]
