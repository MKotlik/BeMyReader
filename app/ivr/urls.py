from django.urls import path

# from ivr.views.main import welcome, welcome_dig, learn_more, login_id, register_start, register_start_dig, register_focus, register_focus_dig, main
from ivr.views.main import *
from ivr.views.login import *
from ivr.views.register import *
from ivr.views.browse_content import browse_content
from ivr.views.browse_requests import browse_requests
from ivr.views.listen import listen
# from ivr.views.request import request_menu, request_title, confirm_request_title, confirm_request_title_dig, request_author, process_request_title
from ivr.views.request import *

urlpatterns = [
    path('welcome', welcome, name='welcome'),
    path('welcome-dig', welcome_dig, name='welcome-dig'),
    path('learn-more', learn_more, name='learn_more'),

    path('login-id', login_id, name='login-id'),

    path('register-start', register_start, name='register-start'),
    path('register-start-dig', register_start_dig, name='register-start-dig'),
    path('register-focus', register_focus, name='register-focus'),
    path('register-focus-dig', register_focus_dig, name='register-focus-dig'),
    path('register-name', register_name, name='register-name'),
    path('register-name-confirm', register_name_confirm, name='register-name-confirm'),
    path('register-name-confirm-dig', register_name_confirm_dig, name='register-name-confirm-dig'),
    path('register-name-process', register_name_process, name='register-name-process'),
    path('register-id', register_id, name='register-id'),
    path('register-id-dig', register_id_dig, name='register-id-dig'),
    path('register-pin', register_pin, name='register-pin'),
    path('register-pin-confirm', register_pin_confirm, name='register-pin-confirm'),
    path('register-pin-confirm-dig', register_pin_confirm_dig, name='register-pin-confirm-dig'),

    path('main', main, name='main'),

    path('browse-content', browse_content, name='browse-content'),
    path('listen', listen, name='listen'),
    path('browse-requests', browse_requests, name='browse-requests'),

    path('request-menu', request_menu, name='request-menu'),
    path('request-title', request_title, name='request-title'),
    path('confirm-request-title', confirm_request_title, name='confirm-request-title'),
    path('confirm-request-title-dig', confirm_request_title_dig,
         name='confirm-request-title-dig'),
   path('request-author', request_author, name='request-author'),
    path('process-request-title', process_request_title, name='process-request-title'),

]
