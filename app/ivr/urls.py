from django.urls import path

# from . import old_views
from ivr.views.main import welcome
from ivr.views.browse_content import browse_content
from ivr.views.browse_requests import browse_requests
from ivr.views.listen import listen
from ivr.views.request import request_menu, request_title, confirm_request_title, confirm_request_title_dig, process_request_title

urlpatterns = [
   path('welcome', welcome, name='welcome'),
   # path('menu', views.menu, name='menu'),
   path('browse-content', browse_content, name='browse-content'),
   path('listen', listen, name='listen'),
   path('browse-requests', browse_requests, name='browse-requests'),
   path('request-menu', request_menu, name='request-menu'),
   path('request-title', request_title, name='request-title'),
   path('confirm-request-title', confirm_request_title, name='confirm-request-title'),
   path('confirm-request-title-dig', confirm_request_title_dig, name='confirm-request-title-dig'),
   path('process-request-title', process_request_title, name='process-request-title'),

]
