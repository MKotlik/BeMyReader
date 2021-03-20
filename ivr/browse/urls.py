# browse/urls.py
from django.urls import path

from . import views

urlpatterns = [
   path('answer', views.browse_content, name='browse-content'),
   path('listen-content', views.listen_content, name='listen-content'),
]