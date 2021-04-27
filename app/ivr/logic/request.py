import os
from urllib.error import URLError
from urllib.request import urlopen

from django.core.files.base import ContentFile
from ivr.models import RecordingType, Request, TempRecording
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

# TODO - implemement a logging framework of some sort

# TODO - write function for getting latest recording

# TODO - use this function to delete any temporary recordings associated with CallSID during call cleanup
# -- except for content recordings, which should be stored in drafts?

# Creates Request object, finding latest TempRecording of type Request_Title matching call_sid
# Deletes TempRecording in same database call (reduce DB operations)
def create_request_delete_temp(call_sid):
    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.REQUEST_TITLE).first()
    
    # TODO - handle None value for temp_title in a better way?
    if temp_title is None:
        print(f"Error: no temporary title recording found for call_sid {call_sid}")
        return None
    
    # TODO - Try returning Request object to view w/o saving. If not, save & return ID
    # -- might be an issue with audio file data disappearing if model not immediately saved
    request_wip = None

    # TODO - handle error with file download (report back to view, not current print statement)
    try:
        # Try downloading file from Twilio
        print(temp_title.recording_url)
        twilio_data = urlopen(temp_title.recording_url).read()
        print(type(twilio_data))

        request_wip = Request(completed=False, title_file=ContentFile(twilio_data, name="title.wav"))

        # Make call to Twilio API to delete the file
        del_remote_recording(temp_title.recording_sid)

        # Delete temp recording from DB
        temp_title.delete()

    except URLError as e:
        print(f"Error while trying to download title audio for call_sid {call_sid}")
        print(e)
    
    return request_wip


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


def del_temp_recording(call_sid, recording_type):
    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=recording_type).first()
    # Delete the temporary recording
    if temp_title is not None:
        temp_title.delete()
