from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import TempRecording, RecordingType, Request
from ivr.logic.request import create_request_delete_temp, del_temp_recording
from ivr.logic.split import split_file
import os

# TODO - make functions to generate the options for all of these interfaces


@csrf_exempt
def record_menu(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    vr = VoiceResponse()

    # TODO - move this into a different pre-menu function (decorator)
    # -- as well as splitting menu and digits processing into separate functions
    auth = request.session.get('auth', None)
    call_sid = request.session.get('call_sid', None)
    print(f"call_sid value in session (from main): {call_sid}")
    print(f"auth value in request (based on login or registration): {auth}")
    auth = True #TODO fix auth to not be passthrough
    if not auth:
        if selected_option is None:
            vr.say("You may only make a recording after logging in")
            with vr.gather(
                action=reverse('record-menu'),
                numDigits=1,
                timeout=5,
            ) as gather:
                gather.say('Press 1, to go to the log-in menu.')
                gather.pause()
                gather.say('Press 9, to return to the main menu.')
            vr.say('We did not receive your selection')
            vr.redirect('main')
        else:
            if selected_option == '1':
                vr.redirect(reverse('login-id'))
            elif selected_option == '9':
                vr.redirect(reverse('main'))
            else:
                vr.say('Sorry, invalid option  ')
                vr.redirect(reverse(''))

    else:  # If authenticated
        # Initial entry to request menu
        if selected_option is None:
            with vr.gather(
                action=reverse('record-menu'),
                numDigits=1,
                timeout=5,
            ) as gather:
                gather.say('Welcome to the Recording Menu.')
                gather.pause()
                gather.say(
                    'Press 1, to make a recording.')
                gather.pause()
                gather.say('Press 9, to return to the main menu.')
            vr.say('We did not receive your selection')
            vr.redirect('')

        # Process key entry from request menu
        else:
            if selected_option == '1':
                vr.redirect(reverse('record-title'))
            elif selected_option == '9':
                vr.redirect(reverse('main'))
            else:
                vr.say('Invalid Entry  ')
                vr.redirect(reverse('record-menu'))

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def record_title(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('''At the tone, please begin your recording.''')
    # TODO - determine if to keep the below msg
    vr.pause(length=2)
    vr.record(
        timeout=10,
        maxLength=1800,
        playBeep=True,
        trim='trim-silence',
        action=reverse('confirm-recording'),
        recordingStatusCallback=reverse('process-record-title')
    )
    return HttpResponse(str(vr), content_type='text/xml')

# TODO this function will need to be rethought for the long form recordings
@csrf_exempt
def confirm_recording(request: HttpRequest) -> HttpResponse:
    call_sid = request.POST.get('CallSid', None)
    vr = VoiceResponse()

    temp_title = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.REQUEST_TITLE).first()

    # If temp_title not found, redirect to keep waiting, count attempt within session
    if not temp_title:
        vr.say('Please wait while we process your recording')
        vr.pause(length=2)
        vr.redirect('')  # redirect back to confirm_recording
        # TODO - count number of tries to confirm title in session (fail and restart after 3)

    else:
        # TODO - add accepting and checking recordingFailed as status

        # Play recording, asking user to confirm or re-record
        vr.say('You recorded')
        vr.play(temp_title.recording_url)  # Construct play verb using recording_url

        with vr.gather(
            action=reverse('confirm-recording-dig'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the recording, and continue.')
            gather.pause()
            gather.say('Press 2, to hear your recording again.')
            gather.pause()
            gather.say('Press 3, to rerecord.')
            gather.pause()
            gather.say('Press 9, to cancel and return to the main menu.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def confirm_recording_dig(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    call_sid = request.POST.get('CallSid', None)
    vr = VoiceResponse()

    if selected_option == '1': # title correct, store and continue
        # Get id of Request object saved in database
        request_id = create_request_delete_temp(call_sid)

        if request_id is not None:
            # TODO - after demo, split into author and details again
            # request.session['request_id'] = request_id
            # vr.say("Great! Now, let's record the author of the work")
            # vr.redirect(reverse('request-author'))

            vr.say("Your recording has been submitted")
            vr.say("Returning to the main menu")
            vr.redirect('main')
        else:
            vr.say('Apologies, there was an application error')
            vr.pause()
            vr.say('Returning to main menu')
            vr.redirect(reverse('main'))

    elif selected_option == '2':  # hear recording again
        vr.redirect(reverse('confirm-recording'))

    elif selected_option == '3':  # redo the recording
        del_temp_recording(call_sid, recording_type=RecordingType.REQUEST_TITLE)
        vr.say("Let's start the recording again")
        vr.redirect(reverse('record-title'))

    elif selected_option == '9':  # Cancel and return to main menu
        del_temp_recording(call_sid, recording_type=RecordingType.REQUEST_TITLE)
        vr.say('Recording cancelled')
        vr.pause()
        vr.say('Returning to main menu')
        vr.redirect(reverse('main'))

    elif selected_option == '*':  # Handle repeat
        with vr.gather(
            action=reverse('confirm-recording-dig'),
            numDigits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the recording, and continue.')
            gather.pause()
            gather.say('Press 2, to hear your recording again.')
            gather.pause()
            gather.say('Press 3, to rerecord.')
            gather.pause()
            gather.say('Press 9, to cancel and return to the main menu.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('confirm-recording')

    else:  # Handle unrecognized option
        vr.say('Sorry, invalid option ')
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


@csrf_exempt
def process_record_title(request: HttpRequest) -> HttpResponse:
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
