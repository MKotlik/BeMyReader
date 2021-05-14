from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import *
import os

# TODO - follow this tutorial to implement play/pause
# https://stackoverflow.com/questions/19880217/twilio-play-pause-resume
@csrf_exempt
def listen(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    content_name = request.session.get('listen_name', '')
    content_id = request.session.get('listen_id', '')
    content_path = request.session.get('listen_path', '')

    # Redirect to same position in list if content name and path not set
    if not (content_name and content_id and content_path):
        vr.say("I'm sorry, there was an error on our end. Returning you to the browse content menu")
        vr.redirect(reverse('browse-content'))
        return HttpResponse(str(vr), content_type='text/xml')

    # Get list of files in this Title's folder
    audio_list = os.listdir(settings.MEDIA_ROOT + '/' + str(content_id))
    first_file = audio_list[0]

    file_url = settings.CUR_URL + content_path + first_file
    print(file_url)

    vr.say('Hello, you are listening to ' + content_name)
    vr.pause(1)
    vr.say('Please wait a moment while the file is loaded')
    vr.play(file_url)
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')
