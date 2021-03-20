from django.db import models

# Create your models here.

class Content(models.Model):
	class Meta:
		verbose_name = 'Content'
		verbose_name_plural = 'Contents'

	requester = models.CharField(max_length=10)
	creator = models.CharField(max_length=10)
	# FIXME: For requestorShould we use django-phonenumber-field
	head = models.TextField()
	body = models.TextField()
	digits = models.PositiveSmallIntegerField(unique=True)
