""" App logic functions (controller code) for managing users
"""
import os
import random
import string
from urllib.error import URLError
from urllib.request import urlopen

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db import IntegrityError
from ivr.models import IVRUser, RecordingType, TempRecording
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

# TODO - look into generating a secure salt (for our application? per user?)

def create_6digit_id():
    """Create random 6 digit ID"""
    return ''.join(random.choices(string.digits, k=6))


# TODO - come up with better way to create user with short, unique ID
def create_IVRUser(num_tries = 10):
    """Attempt to create and return an IVRUser object with a unique, 6 digit id"""
    created = False
    attempt = 0
    user = None

    while not created and attempt < num_tries:
        try:
            id = create_6digit_id()
            user = IVRUser.objects.create(id=id)
            created = True
        except IntegrityError:
            # TODO - remove after testing
            attempt += 1
            print(f"Caught {attempt} IntegrityError trying to create user. Trying again")

    if not created:
        print("Error: Couldn't create user with unique ID")

    return user


def register_IVRUser_initial(user_id, phone_number, country, language, focus):
    """Update a given IVRUser object with an initial set of fields (from first registration step)"""
    user = IVRUser.objects.get(id=user_id)
    user.latest_number = phone_number
    user.latest_country = country
    user.language = language
    user.focus = focus
    user.save()
    return user


def hash_IVRUser_pin(raw_pin):
    # TODO - stop using hardcoded salt!
    salt = 'T3rr1bl3S@lt'
    return make_password(raw_pin, salt)


# TODO - revert after fixing authentication issue
def register_IVRUser_final(user_id, raw_pin):
    print(f"register final on id: {user_id}")
    user = IVRUser.objects.get(id=user_id)
    print(f"registering this user object: {user}")
    # user.hashed_pin = make_password(raw_pin)
    user.raw_pin = raw_pin
    user.register_complete = True
    user.save()


# TODO - revert after fixing authentication issue
def check_IVRUser_auth(user_id, raw_pin):
    auth = False
    user = IVRUser.objects.filter(id=user_id).first()
    print(f"check_auth user {user}")
    if user is not None:
        # hashed_pin = hash_IVRUser_pin(raw_pin)
        # auth = (user.hashed_pin == hashed_pin)
        auth = (user.raw_pin == raw_pin)
    return auth


def update_user_name_del_temp_recording(user_id, call_sid):
    """Set name audio file of user with given id, finding latest TempRecording of type Request_Title matching given call_sid.
    Delete the corresponding TempRecording from the database.
    Return whether successfully updated with name audio (bool)"""
    temp_name = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.ACCOUNT_NAME).first()
    
    # TODO - handle None value for temp_title in a better way?
    if temp_name is None:
        print(f"Error: no temporary title recording found for call_sid {call_sid}")
        return None
    
    success = False

    # TODO - handle error with file download (report back to view, not current print statement)
    try:
        # Try downloading file from Twilio
        print(temp_name.recording_url)
        twilio_data = urlopen(temp_name.recording_url).read()
        print(type(twilio_data))

        # Find user and update with audio

        user = IVRUser.objects.get(id=user_id)
        user.name_file=ContentFile(twilio_data, name="name.wav")
        user.save()
        success = True

        # Make call to Twilio API to delete the file
        del_remote_recording(temp_name.recording_sid)

        # Delete temp recording from DB
        temp_name.delete()

    except URLError as e:
        print(f"Error while trying to download name audio for call_sid {call_sid}")
        print(e)
    
    return success


# TODO - redundant, also in request.py. Make separate TempRecording logic class
# Delete recording with given sid from Twilio account, return success as bool
def del_remote_recording(recording_sid):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if account_sid is None or auth_token is None:
        print("Error: Twilio credentials not loaded from system environment")
        return False

    try:
        client = Client(account_sid, auth_token)
        return client.recordings(recording_sid).delete()
    except TwilioRestException as e:
        print(f"Error while trying to delete recording with sid {recording_sid}")
        print(e)
        return False


# TODO - redundant, also in request.py. Make separate TempRecording logic class
def del_temp_recording(call_sid, recording_type):
    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=recording_type).first()
    # Delete the temporary recording
    if temp_title is not None:
        temp_title.delete()
