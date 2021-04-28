from django.db import models

# Create your models here.
import os
from django.db import models
from django.conf import settings


# NOTE - consider moving controller logic into Models, out of logic module


# Whether a user is mainly client or volunteer
class UserFocus(models.TextChoices):
    CLIENT = 'CL'
    VOLUNTEER = 'VO'


class IVRUser(models.Model):
    class Meta:
        verbose_name = 'IVR User'
        verbose_name_plural = 'IVR Users'

    # TODO - figure out better way of getting each users a unique, memorable ID
    # -- ID is currently not auto-generated, must be given by users
    id = models.CharField("ID", max_length=6, primary_key=True)

    # TODO - store salt as well
    hashed_pin = models.CharField("Hashed Pin", max_length=128)

    # Whether completed registration, or in progress
    register_complete = models.BooleanField("Completed Registration?", default=False)

    focus = models.CharField(
        "User Focus", max_length=2, choices=UserFocus.choices,
        default=UserFocus.CLIENT, blank=True)

    # Phone Number user LAST called from
    latest_number = models.CharField("Latest Phone Number", max_length=15)

    # Country of user's LAST phone number (based on Twilio info)
    latest_country = models.CharField("Latest Country", max_length=40)

    # Interface language
    # TODO - internationalize our application and limit to a number of Choices
    # TODO - ask user to set/update language based on phone number country
    language = models.CharField("Interface Langauge", max_length=5, default="en")

    # Account creation time and last login time (automatic)
    created_at = models.DateTimeField(auto_now_add=True)
    login_at = models.DateTimeField(auto_now=True)

    # Generate file path from user ID
    def user_directory_path(self, filename):
        # file will be uploaded to MEDIA_ROOT/users/<id>/filename
        return f"users/{self.id}/{filename}"

    # User's name/username recorded as voice
    name_file = models.FileField("Name Audio File", upload_to=user_directory_path, blank=True)

    # Additional methods
    def __str__(self):
        return f"IVRUser w/ ID {self.id}"


class RecordingType(models.TextChoices):
    ACCOUNT_NAME = 'AN'
    REQUEST_TITLE = 'RT'
    REQUEST_AUTHOR = 'RA'
    REQUEST_DETAILS = 'RD'


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
    def __str__(self):
        return f"TempRecording w/ SID {self.recording_sid} for CallSID {self.call_sid}"


class Request(models.Model):
    class Meta:
        verbose_name = 'Request for Content'
        verbose_name_plural = 'Requests for Content'

    # ID is automatically generated

    # Generate file path from request ID
    def request_directory_path(self, filename):
        # file will be uploaded to MEDIA_ROOT/requests/<id>/filename
        return f"requests/{self.id}/{filename}"

    # Whether user has completed creating their request
    # TODO - test if can store incomplete (unsaved) record in session
    completed = models.BooleanField("Request Completed", default=False)

    # TODO - add reference to source User

    # Paths to title, author, and details audio files
    title_file = models.FileField("Title Audio File", upload_to=request_directory_path, blank=True)
    author_file = models.FileField(
        "Author Audio File", upload_to=request_directory_path, blank=True)
    details_file = models.FileField(
        "Details Audio File", upload_to=request_directory_path, blank=True)

    # Record creation and modification time for ordering
    # TODO - decide whether to use created_at or modified_at
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Additional methods
    def __str__(self):
        return f"Request w/ ID {self.id}"


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
