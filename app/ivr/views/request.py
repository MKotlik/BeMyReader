from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import TempRecording, RecordingType, Request
from ivr.logic.request import create_request_delete_temp, del_temp_recording
import os

# TODO - make functions to generate the options for all of these interfaces


@csrf_exempt
def request_menu(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    vr = VoiceResponse()

    # Initial entry to request menu
    if selected_option is None:
        with vr.gather(
            action=reverse('request-menu'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Welcome to the Make Request Menu.')
            gather.pause()
            gather.say(
                'Press 1, to make a request for new content.')
            gather.pause()
            gather.say('Press 9, to return to the main menu.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    # Process key entry from request menu
    else:
        if selected_option == '1':
            vr.redirect(reverse('request-title'))
        elif selected_option == '9':
            vr.redirect(reverse('welcome'))
        else:
            vr.say('Invalid Entry  ')
            vr.redirect(reverse('request-menu'))

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def request_title(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('''Please limit your request to 20 seconds or less, and press any
            key once you are finished speaking.''')
    vr.pause()
    vr.say('''At the tone, please say the title, author, and any details of the
            work you are requesting.''')
    # TODO - determine if to keep the below msg
    vr.pause(length=2)
    vr.record(
        timeout=10,
        maxLength=20,
        playBeep=True,
        trim='trim-silence',
        action=reverse('confirm-request-title'),
        recordingStatusCallback=reverse('process-request-title')
    )
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def confirm_request_title(request: HttpRequest) -> HttpResponse:
    call_sid = request.POST.get('CallSid', None)
    vr = VoiceResponse()

    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.REQUEST_TITLE).first()

    # If temp_title not found, redirect to keep waiting, count attempt within session
    if not temp_title:
        vr.say('Please wait while we process your recording')
        vr.pause(length=5)
        vr.redirect('')  # redirect back to confirm_request_title
        # TODO - count number of tries to confirm title in session (fail and restart after 3)

    else:
        # TODO - add accepting and checking recordingFailed as status

        # Play recording, asking user to confirm or re-record
        vr.say('You recorded')
        vr.play(temp_title.recording_url)  # Construct play verb using recording_url

        with vr.gather(
            action=reverse('confirm-request-title-dig'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the request is correct, and continue.')
            gather.pause()
            gather.say('Press 2, to hear your request again.')
            gather.pause()
            gather.say('Press 3, to rerecord your request.')
            gather.pause()
            gather.say('Press 9, to cancel and return to the main menu.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def confirm_request_title_dig(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    call_sid = request.POST.get('CallSid', None)
    vr = VoiceResponse()

    if selected_option == '1': # title correct, store and continue
        # Get id of Request object saved in database
        request_id = create_request_delete_temp(call_sid)
        print(request_id)
        if request_id is not None:
            request.session['request_id'] = request_id
            vr.say("Great! Now, let's record the author of the work")
            vr.redirect(reverse('request-author'))
        else:
            vr.say('Apologies, there was an application error')
            vr.pause()
            vr.say('Returning to main menu')
            vr.redirect(reverse('welcome'))

    elif selected_option == '2':  # hear recording again
        vr.redirect(reverse('confirm-request-title'))

    elif selected_option == '3':  # redo the recording
        del_temp_recording(call_sid, recording_type=RecordingType.REQUEST_TITLE)
        vr.say("Let's record the title again")
        vr.redirect(reverse('request-title'))

    elif selected_option == '9':  # Cancel and return to main menu
        del_temp_recording(call_sid, recording_type=RecordingType.REQUEST_TITLE)
        vr.say('Request cancelled')
        vr.pause()
        vr.say('Returning to main menu')
        vr.redirect(reverse('welcome'))

    elif selected_option == '*':  # Handle repeat
        with vr.gather(
            action=reverse('confirm-request-title-dig'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the request is correct, and continue.')
            gather.pause()
            gather.say('Press 2, to hear your request again.')
            gather.pause()
            gather.say('Press 3, to rerecord your request.')
            gather.pause()
            gather.say('Press 9, to cancel and return to the main menu.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    else:  # Handle unrecognized option
        vr.say('Invalid entry ')
        with vr.gather(
            action=reverse('confirm-request-title-dig'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the request is correct, and continue.')
            gather.pause()
            gather.say('Press 2, to hear your request again.')
            gather.pause()
            gather.say('Press 3, to rerecord your request.')
            gather.pause()
            gather.say('Press 9, to cancel and return to the main menu.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def request_author(request: HttpRequest) -> HttpResponse:
    # NOTE - just testing whether model can be stored in session right now
    # NOTE - And files used to play back content
    # TODO - finish implementing request author
    request_id = request.session.get('request_id', None)
    vr = VoiceResponse()
    if request_id is None:
        print("MISHA THE REQUEST_ID IS NONE!!!!")
        vr.say("Hoooooooow is the request None?!")
    else:
        request_wip = Request.objects.get(id=request_id)
        if request_wip.completed is False:
            vr.say("Request still not completed")
        else:
            vr.say("How is the request completed? Whaaaaaaaaat?")

        vr.say("Trying to play the audio file of the request for testing purposes")
        vr.play(request_wip.title_file.url)
        vr.say("We'll do the rest later")
        vr.hangup()

    return HttpResponse(str(vr), content_type='text/xml')


# @csrf_exempt
# def confirm_request_author(request: HttpRequest) -> HttpResponse:
#     call_sid = request.POST.get('CallSid', None)
#     request_wip = request.session.get('request_wip', None)
#     vr = VoiceResponse()

#     temp_title = TempRecording.objects.order_by('created_at').filter(
#         call_sid=call_sid, recording_type=RecordingType.REQUEST_TITLE).first()

#     # If temp_title not found, redirect to keep waiting, count attempt within session
#     if not temp_title:
#         vr.say('Please wait while we process your recording')
#         vr.pause(length=5)
#         vr.redirect('')  # redirect back to confirm_request_title
#         # TODO - count number of tries to confirm title in session (fail and restart after 3)

#     else:
#         # TODO - add accepting and checking recordingFailed as status

#         # Play recording, asking user to confirm or re-record
#         vr.say('You recorded')
#         print(temp_title.recording_url)
#         vr.play(temp_title.recording_url)  # Construct play verb using recording_url

#         with vr.gather(
#             action=reverse('confirm-request-title-dig'),
#             numDigits=1,
#             timeout=5,
#         ) as gather:
#             gather.say('Press 1, to confirm the title is correct and continue.')
#             gather.say('Press 2, to hear the recording again.')
#             gather.say('Press 3, to record the title again.')
#             gather.say('Press 9, to cancel and return to the main menu.')
#             gather.say('Press star, to repeat these options.')
#         vr.say('We did not receive your selection')
#         vr.redirect('')

#     return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def process_request_title(request: HttpRequest) -> HttpResponse:
    call_sid = request.POST.get('CallSid', None)
    recording_sid = request.POST.get('RecordingSid', None)
    recording_url = request.POST.get('RecordingUrl', None)

    recording_status = request.POST.get('RecordingStatus', None)

    # TODO - test recording status being failed

    # Create TempRecording in DB
    temp_recording = TempRecording(call_sid=call_sid,
                                   recording_type=RecordingType.REQUEST_TITLE,
                                   failed=(recording_status == 'failed'),
                                   recording_sid=recording_sid,
                                   recording_url=recording_url)
    temp_recording.save()

    return HttpResponse("", content_type='text/xml')
