from urllib.request import urlopen
from urllib.error import URLError
from django.core.files import ContentFile
from ivr.models import TempRecording, RecordingType, Request

# TODO - write function for getting latest recording

# TODO - use this function to delete any temporary recordings associated with CallSID during call cleanup
# -- except for content recordings, which should be stored in drafts?

# Creates Request object, finding latest TempRecording of type Request_Title matching call_sid
# Deletes TempRecording in same database call (reduce DB operations)
def create_request_delete_temp(call_sid):
    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.REQUEST_TITLE).first()
    
    # TODO - Try returning Request object to view w/o saving. If not, save & return ID
    # -- might be an issue with audio file data disappearing if model not immediately saved
    request_wip = None
    
    # TODO - handle None value for temp_title (report back to view)
    # TODO - handle error with file download (report back to view, not current print statement)
    # Try downloading file from Twilio
    try:
        print(temp_title.recording_url)
        twilio_data = urlopen(temp_title.recording_url).read()
        print(type(twilio_data))

        request_wip = Request(completed=False, title_file=ContentFile(twilio_data, name="title.wav"))

        # Make call to Twilio API to delete the file
        
    except URLError:
        print("Error: Could not download request title audio from Twilio")
    
    return request_wip




def del_temp_recording(call_sid, recording_type):
    # TODO - improve this to get specifically the latest request title recording for given SID
    # temp_recordings = TempRecording.objects.order_by('created_at').filter(call_sid=call_sid)
    # temp_title = None
    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=recording_type).first()

    # Check if some matching temp_recording matches call_sid
    # if temp_recordings:
    #     # Get the single top temporary recording matching call_sid
    #     for cnt, title in enumerate(temp_recordings):
    #         if cnt > 0:
    #             break
    #         temp_title = title

    # Delete the temporary recording
    if temp_title is not None:
        temp_title.delete()
