from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from django.conf import settings
from django.conf.urls.static import static

file_url = "https://4f704a9cb4be.ngrok.io/media/Count%20Zero%2001.mp3"

@csrf_exempt
def answer(request: HttpRequest) -> HttpResponse:
    #file_url = settings.MEDIA_URL + request[filename]
    vr = VoiceResponse()
    vr.say('Hello, please wait just a moment while the file is loaded.')
    vr.play(file_url)
    return HttpResponse(str(vr), content_type='text/xml')
