from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import UserFocus, IVRUser


@csrf_exempt
# TODO - Michael, finish implementing
def login_id(request: HttpRequest) -> HttpResponse:
    """View for logging in to an existing account"""
    vr = VoiceResponse()
    vr.say("Not yet implemented")
    vr.hangup()
    return HttpResponse(str(vr), content_type='text/xml')