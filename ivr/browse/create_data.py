from browse.models import *
from django.db import models
from django.conf import settings

Title.objects.create(
    name="count zero",
    author="william gibson",
    genre='LI',
    files=models.FilePathField(path=settings.MEDIA_ROOT+'/0/')
)

Title.objects.create(
    name="mona lisa overdrive",
    author="william gibson",
    genre="LI",
    files=models.FilePathField(path=settings.MEDIA_ROOT+'/1/')
)


"""
Content.objects.create(head='Entry 1', body='Content for Entry 1')
Content.objects.create(head='Entry 2', body='Content for Entry 2')
Content.objects.create(head='Entry 3', body='Content for Entry 3')
Content.objects.create(head='Entry 4', body='Content for Entry 4')
Content.objects.create(head='Entry 5', body='Content for Entry 5')
Content.objects.create(head='Entry 6', body='Content for Entry 6')
Content.objects.create(head='Entry 7', body='Content for Entry 7')
Content.objects.create(head='Entry 8', body='Content for Entry 8')
Content.objects.create(head='Entry 9', body='Content for Entry 9')
Content.objects.create(head='Entry 10', body='Content for Entry 10')

Content.objects.create(head='Math Algebra', body='Content for Math Algebra')
Content.objects.create(head='Science Chemistry', body='Content for Science Chemistry')
Content.objects.create(head='Science Biology', body='Content for Science Biology')
Content.objects.create(head='Literature Shakespeare', body='Content for Literature Shakespeare')
Content.objects.create(head='Math Calculus', body='Content for Math Calculus')
Content.objects.create(head='Literature American', body='Content for Literature American')
Content.objects.create(head='History World', body='Content for History World')
Content.objects.create(head='History Ancient', body='Content for History Ancient')
Content.objects.create(head='Math Geometry', body='Content for Math Geometry')
Content.objects.create(head='Literature Fiction', body='Literature Fiction')
"""
