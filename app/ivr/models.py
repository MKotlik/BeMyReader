from django.db import models

# Create your models here.
import os
from django.db import models
from django.conf import settings


"""
class User(models.Model):
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
	# user entered
    name = models.CharField("name", max_length=30, null=True)
    passcode = models.CharField("passcode", max_length=6, null=True)
	# grab from twilio any time someone connects
    number = models.CharField("phone number", max_length=15)
"""

# class IVRUser(models.Model):
#     class Meta:
#         verbose_name = 'IVR User'
#         verbose_name_plural = 'IVR Users'

#     # Generate path from user ID
#     @staticmethod
#     def user_directory_path(instance, filename):
#         # file will be uploaded to MEDIA_ROOT/users/user_<id>/filename
#         return f"users/user{instance."


class RecordingType(models.TextChoices):
    ACCOUNT_NAME = 'AN'
    REQUEST_TITLE = 'RT'
    REQUEST_AUTHOR = 'RA'
    REQUEST_DETAILS = 'RD'

#     # Grabbed from Twilio, must be unique, used to find user object
#     number = models.CharField("phone number", max_length=15, primary_key=True)

#     # Recordings provided by user
#     name_audio = models.FileField()


class TempRecording(models.Model):
    class Meta:
        verbose_name = 'Twilio Recording in Queue'
        verbose_name_plural = 'Twilio Recordings in Queue'

    # ID is automatically generated
    # Look up by callSid
    call_sid = models.CharField("CallSid", max_length=34)

    # State whether recording failed
    failed = models.BooleanField("Recording Failed", default=False)

    # Give source of recording in user flow
    recording_type = models.CharField(
        "Recording Type", max_length=2, choices=RecordingType.choices,
        default=RecordingType.REQUEST_TITLE)

    # Provide recording_sid and recording_url (which can be null if call failed)
    recording_sid = models.CharField("CallSid", max_length=34, blank=True)
    recording_url = models.URLField("CallSid", max_length=255, blank=True)

    # Record creation time for ordering if multiple recordings with same SID
    created_at = models.DateTimeField(auto_now_add=True)

    # Methods
    def __unicode__(self):
        return f"TempRecording w/ SID {self.recording_sid} for CallSID {self.call_sid}"
    # NOTE - consider putting delete call to Twilio API here in .delete method


class Request(models.Model):
    class Meta:
        verbose_name = 'Request for Content'
        verbose_name_plural = 'Requests for Content'

    # Generate path from request ID
    @staticmethod
    def request_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/requests/<id>/filename
        return f"users/{instance.id}/{filename}"

    # ID is automatically generated

    # Whether user has completed creating their request
    # TODO - test if can store incomplete (unsaved) record in session
    completed = models.BooleanField("Request Completed", default=False)

    # TODO - add reference to source User

    # Paths to title, author, and details audio files
    title_file = models.FileField("Title Audio File", upload_to=request_directory_path)
    author_file = models.FileField(
        "Author Audio File", upload_to=request_directory_path, blank=True)
    details_file = models.FileField(
        "Details Audio File", upload_to=request_directory_path, blank=True)

    # Record creation and modification time for ordering
    # TODO - decide whether to use created_at or modified_at
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


# TODO - remove after deprecating
class Title(models.Model):
    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'
    GENRES = [
        ('SC', 'Science'),
        ('HI', 'History'),
        ('LI', 'Literature'),
        ('MA', 'Math'),
        ('BI', 'Biography'),
        ('RE', 'Reference'),
    ]
    # user entered
    name = models.CharField("book title", max_length=50, null=True)
    author = models.CharField("book author", max_length=50, null=True)
    # reader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    genre = models.CharField("genre", max_length=2, choices=GENRES, null=True)
    # auto generated
    files = models.CharField("file path", max_length=200)
