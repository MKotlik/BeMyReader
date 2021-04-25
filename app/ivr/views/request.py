from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import *
import os


@csrf_exempt
def request_menu(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    vr = VoiceResponse()

    # Initial entry to request menu
    if selected_option is None:
        with vr.gather(
            action=reverse('request-menu'),
            timeout=1,
        ) as gather:
            gather.say('Welcome to the Make Request Menu')
            gather.say('Press 1, if you would like to record a request to transcribe some text.')
            gather.say('Press 9, to return to the main menu.')
        vr.say('We did not receive your selection')
        vr.redirect('')
        
    # Process key entry from request menu
    else:
        if selected_option is '1':
            vr.redirect(reverse('request-title'))
        elif selected_option is '9':
            vr.redirect(reverse('welcome'))
        else:
            vr.say('Invalid Entry  ')
            vr.redirect(reverse('request-menu'))

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def request_title(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('At the tone, please say the name, and edition or year of the work you would'
            ' like to have read.')
    vr.pause()
    # TODO - determine if to keep the below msg
    vr.say('Please keep your recording 20 seconds or less')
    vr.say('And press any key once you are finished.')
    vr.pause(length=2)
    vr.record(
        timeout=10,
        maxLength=20,
        playBeep=True,
        trim='trim-silence',
        action=reverse('confirm-request-title'),
        recordingStatusCallback=reverse('process-request-title')
    )
    vr.say('We did not receive your selection')
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def confirm_request_title(request: HttpRequest) -> HttpResponse:
    pass


@csrf_exempt
def confirm_request(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Would confirm request here')
    vr.hangup()
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def process_request(request: HttpRequest) -> HttpResponse:
    recording_sid = request.POST.get('RecordingSid', None)
    recording_url = request.POST.get('RecordingUrl', None)
    recording_status = request.POST.get('RecordingStatus', None)
    print(f"Status: {recording_status}")
    print(f"For SID: {recording_sid} at {recording_url}")
    # TODO - return an empty response