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
    language = models.CharField("Interface Language", max_length=5, default="en")

    # Account creation time and last login time (automatic)
    created_at = models.DateTimeField(auto_now_add=True)
    login_at = models.DateTimeField(auto_now=True)

    # Generate file path from user ID
    def user_directory_path(self, filename):
        # file will be uploaded to MEDIA_ROOT/users/<id>/filename
        return f"users/{self.id}/{filename}"

    # User's name/username recorded as voice
    name_file = models.FileField("Name Audio File", upload_to=user_directory_path, blank=True)

    # TODO - consider how links to user's requests and content could be stored in their record (currently relying on their ForeignKeys)

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
    
    # ForeignKey to the user that created the request
    # TODO - figure out how to delete with outstanding request if user deletes (cancel request? assign request to default user and notify volunteer?)
    # TODO - make null=False and blank=False after confirming everyone has reset their databases
    creator = models.ForeignKey(IVRUser, on_delete=models.CASCADE, null=True, blank=True)

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


class Content(models.Model):
    class Meta:
        verbose_name = 'Content'
        verbose_name_plural = 'Content'

    # ForeignKey to the user that's recording this content
    # TODO - figure out how to handle content if user deleted
    # Should leave it if completed, but delete if in-progress?
    creator = models.ForeignKey(IVRUser, on_delete=models.SET_NULL, null=True)

    # ForeignKey to the original request for the content
    # TODO - decide whether volunteer can create Content not tied to a request
    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True)

    # Whether the user has completed recording the metadata for this content (ex. title)
    meta_recorded = models.BooleanField("Metadata Recorded", default=False)

    # Whether recording has been completed and published/shared
    published = models.BooleanField("Content Published", default=False)

    # Content language
    # TODO - internationalize our application and limit to a number of Choices
    language = models.CharField("Content Language", max_length=5, default="en")

    # Length of the Content (all sections included, in seconds)
    length = models.PositiveSmallIntegerField("Content Length", blank=True)

    # Generate file path from content ID
    def content_directory_path(self, filename):
        # files will be uploaded to MEDIA_ROOT/content/<id>/filename
        return f"content/{self.id}/{filename}"

    # Paths to title, author, and details audio files
    # Should be named title.wav, author.wav, and details.wav
    title_file = models.FileField("Title Audio File", upload_to=content_directory_path, blank=True)
    author_file = models.FileField(
        "Author Audio File", upload_to=content_directory_path, blank=True)
    details_file = models.FileField(
        "Details Audio File", upload_to=content_directory_path, blank=True)

    # NOTE - constituent Sections are found by their content ForeignKey

    # Record creation and modification time for ordering
    # TODO - decide whether to use created_at or modified_at
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Additional methods
    def __str__(self):
        return f"Content w/ ID {self.id}"


class Section(models.Model):
    class Meta:
        verbose_name = 'section'
        verbose_name_plural = 'sections'

    # ForeignKey to the user that's recording this section
    # TODO - figure out how to handle section if user deleted
    # Should leave it if completed, but delete if in-progress?
    creator = models.ForeignKey(IVRUser, on_delete=models.SET_NULL, null=True)

    # ForeignKey to the parent Content for this Section
    # Deleting the section if the Content is deleted
    # TODO - should write a .delete (cleanup) method that deletes the audio files
    # TODO - set null=True after everyone resets their databases
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=True)

    # Position of the Section within the order of all Sections in the Content
    position = models.PositiveSmallIntegerField("Position of the section in the Content", blank=True)

    # Length of the Section (in seconds)
    length = models.PositiveSmallIntegerField("Content Length", blank=True)

    # Generate file path from ID of parent Content record
    # Use content_directory path to get full paths to files with names listed in segment_files
    def content_directory_path(self, filename):
        # files will be uploaded to MEDIA_ROOT/content/<id>/filename
        # TODO check that self.content.id works
        return f"content/{self.content.id}/{filename}"

    # Paths to section Title audio file
    # Should be named title.wav
    title_file = models.FileField("Title Audio File", upload_to=content_directory_path, blank=True)

    # TODO - might not be correct. Test to see that storing names of segment files as lists works
    # TODO - check that a length of 150 is sufficient
    segment_files = models.CharField("Names of Segment Files", max_length=150, blank=True)

    # Record creation and modification time for ordering
    # TODO - decide whether to use created_at or modified_at
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Additional methods
    def __str__(self):
        return f"Segment w/ ID {self.id}, part of Content w/ id {self.content.id}"
