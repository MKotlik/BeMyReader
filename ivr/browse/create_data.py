from browse.models import *
from django.db import models
from django.conf import settings

Title.objects.create(
    name="neuromancer",
    author="william gibson",
    genre='LI',
    files=settings.MEDIA_URL+'0/'
)

Title.objects.create(
    name="count zero",
    author="william gibson",
    genre='LI',
    files=settings.MEDIA_URL+'1/'
)

Title.objects.create(
    name="mona lisa overdrive",
    author="william gibson",
    genre="LI",
    files=settings.MEDIA_URL+'2/'
)
