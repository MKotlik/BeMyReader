from django.urls import path

# from . import old_views
from ivr.views.main import welcome
from ivr.views.browse_content import browse_content
from ivr.views.browse_requests import browse_requests
from ivr.views.listen import listen
from ivr.views.request import request_content

urlpatterns = [
   path('welcome', welcome, name='welcome'),
   # path('menu', views.menu, name='menu'),
   path('browse-content', browse_content, name='browse-content'),
   path('listen', listen, name='listen'),
   path('browse-requests', browse_requests, name='browse-requests'),
   path('request-content', request_content, name='request-content'),
]
