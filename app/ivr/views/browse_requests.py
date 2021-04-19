from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import *
import os


@csrf_exempt
def browse_requests(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Welcome to the Browse Requests Menu')
    vr.say('Sorry, under construction')
    vr.redirect(reverse('welcome'))
    return HttpResponse(str(vr), content_type='text/xml')