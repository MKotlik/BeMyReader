"""Registration interface: view presentation and entry handling functions, callbacks"""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import UserFocus, IVRUser, RecordingType, TempRecording
from ivr.logic.user import create_IVRUser, update_user_name_del_temp_recording, register_IVRUser_initial, register_IVRUser_final, del_temp_recording

@csrf_exempt
def register_start(request: HttpRequest) -> HttpResponse:
    """View for logging in to an existing account"""
    vr = VoiceResponse()
    vr.say('Creating a BeMyReader account will allow you to request content, '
            're-chord content, and more.')
    vr.pause()
    vr.say('However, you can also browse and listen to existing content without an account')
    vr.pause()
    with vr.gather(
                action=reverse('register-start-dig'),
                #finish_on_key='#',
                num_digits=1,
                timeout=5,
        ) as gather:
            gather.say('How would you like to proceed?')
            gather.say('Press 1, to continue creating an account')
            gather.pause()
            gather.say('Press 9, to return to the welcome menu')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
    vr.say('We did not receive your selection')
    vr.redirect(reverse('register-start'))
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_start_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for register_start view"""
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)

    if selected_option == '1':  # proceed with registration
        vr.say("Great!")
        vr.redirect(reverse('register-focus'))
    
    elif selected_option == '9':  # return to welcome menu
        vr.redirect(reverse('welcome'))

    elif selected_option == '*':  # repeat selected
        with vr.gather(
                action=reverse('register-start-dig'),
                #finish_on_key='#',
                num_digits=1,
                timeout=5,
        ) as gather:
            gather.say('How would you like to proceed?')
            gather.say('Press 1, to continue creating an account')
            gather.pause()
            gather.say('Press 9, to return to the welcome menu')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
        vr.say('We did not receive your selection')
        vr.redirect(reverse('register-start'))
    
    else:
        vr.say("Sorry, invalid option")
        vr.redirect(reverse('register-start'))
    
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_focus(request: HttpRequest) -> HttpResponse:
    """View for actually creating an account, starting with user focus"""
    vr = VoiceResponse()
    user = create_IVRUser()

    # NOTE - will need to handle account creation failure (ex. ID collision, better)
    if user is None:
        vr.say("We are sorry, we cannot create an account due to an application error.")
        vr.pause()
        vr.say("For now, you will continue as a guest")
        vr.redirect(reverse('main'))  # Note, the redirect bypasses the flow below
    else:
        request.session['user_id'] = user.id

    vr.say("Now, how would you like to use this platform?")
    with vr.gather(
                action=reverse('register-focus-dig'),
                #finish_on_key='#',
                num_digits=1,
                timeout=5,
        ) as gather:
            gather.say('Press 1, if you will mainly be browsing, listening to, and requesting content')
            gather.pause()
            gather.say('Press 2, if you are sighted and might also like to volunteer to record content')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
    vr.say('We did not receive your selection')
    vr.redirect(reverse('register-focus'))
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_focus_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for register_focus view"""
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)

    if selected_option in ['1', '2']:  # update user account with initial fields
        user_id = request.session.get('user_id', None)
        phone_number = request.POST.get('From', None)
        country = request.POST.get('FromCountry', None)
        language = "en"
        focus = UserFocus.CLIENT if selected_option == '1' else UserFocus.VOLUNTEER

        register_IVRUser_initial(user_id, phone_number, country, language, focus)
        vr.redirect(reverse('register-name'))

    elif selected_option == '*':  # repeat selected
        with vr.gather(
                action=reverse('register-focus-dig'),
                #finish_on_key='#',
                numDigits=1,
                timeout=5,
        ) as gather:
            gather.say('Press 1, if you will mainly be browsing, listening to, and requesting content')
            gather.pause()
            gather.say('Press 2, if you are sighted and might also like to volunteer to record content')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
        vr.say('We did not receive your selection')
        vr.redirect(reverse('register-focus'))
    
    else:
        vr.say("Sorry, invalid option")
        vr.redirect(reverse('register-focus'))
    
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_name(request: HttpRequest) -> HttpResponse:
    """View for recording the name audio for a user account"""
    vr = VoiceResponse()

    vr.say("Now we will need to record a name, to identify you to other users on BeMyReader.")
    vr.pause()
    vr.say("At the tone, please say your full name, or a nickname, or a clever username")
    vr.pause()
    vr.say("Please keep it clean, under 10 seconds, and press any key once you are finished.")
    vr.pause(length=2)
    vr.record(
        timeout=5,
        max_length=10,
        playBeep=True,
        trim='trim-silence',
        action=reverse('register-name-confirm'),
        recordingStatusCallback=reverse('register-name-process')
    )
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_name_confirm(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    call_sid = request.POST.get('CallSid', None)

    temp_name = TempRecording.objects.order_by('created_at').filter(
        call_sid=call_sid, recording_type=RecordingType.ACCOUNT_NAME).first()

    # If temp_name not found, redirect to keep waiting, count attempt within session
    if not temp_name:
        vr.say('Please wait while we process your recording')
        vr.pause(length=2)
        vr.redirect('')  # redirect back to register_name_confirm
        # TODO - count number of tries to confirm name in session (fail and restart after 3)

    else:
        # TODO - add accepting and checking recordingFailed as status

        # Play recording, asking user to confirm or re-record
        vr.say('You recorded')
        vr.play(temp_name.recording_url)  # Construct play verb using recording_url

        with vr.gather(
            action=reverse('register-name-confirm-dig'),
            num_digits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the name is correct and continue.')
            gather.pause()
            gather.say('Press 2, to hear the recording again.')
            gather.pause()
            gather.say('Press 3, to record your name again.')
            gather.pause()
            gather.say('Or, press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('')

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_name_confirm_dig(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)
    call_sid = request.POST.get('CallSid', None)
    user_id = request.session.get('user_id', None)

    if selected_option == '1': # title correct, store and continue
        success = update_user_name_del_temp_recording(user_id, call_sid)

        if success:
            vr.say("Great! We are almost done.")
            vr.redirect(reverse('register-id'))
        else:
            # TODO - HANDLE NAME CREATION FAILURE BETTER, CLEAN UP DB
            vr.say('Apologies, there was an application error')
            vr.pause()
            vr.say('Returning to welcome menu')
            vr.redirect(reverse('welcome'))

    elif selected_option == '2':  # hear recording again
        vr.redirect(reverse('register-name-confirm'))

    elif selected_option == '3':  # redo the recording
        del_temp_recording(call_sid, recording_type=RecordingType.ACCOUNT_NAME)
        vr.say("Let's record your name again")
        vr.redirect(reverse('register-name'))

    elif selected_option == '*':  # Handle repeat
        with vr.gather(
            action=reverse('register-name-confirm-dig'),
            num_digits=1,
            timeout=5,
        ) as gather:
            gather.say('Press 1, to confirm the name is correct and continue.')
            gather.pause()
            gather.say('Press 2, to hear the recording again.')
            gather.pause()
            gather.say('Press 3, to record your name again.')
            gather.pause()
            gather.say('Or, press star, to repeat these options.')
        vr.say('We did not receive your selection')
        vr.redirect('register-name-confirm')

    else:  # Handle unrecognized option
        vr.say("Sorry, invalid option")
        vr.redirect(reverse('register-name-confirm'))

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_id(request: HttpRequest) -> HttpResponse:
    """View for giving user the id to their account"""
    vr = VoiceResponse()
    user_id = request.session.get('user_id', None)
    id_str = ', '.join(user_id)

    vr.say("Please write down the following, 6 digit user ID")
    vr.pause()
    vr.say("You will need this ID to access your account, so do not lose it.")
    vr.pause()
    vr.say("You may replay it as many times as you need.")
    with vr.gather(
        action=reverse('register-id-dig'),
        num_digits=1,
        timeout=5,
    ) as gather:
        gather.say(f"Your ID    is, {id_str}")
        gather.pause(length=2)
        gather.say('Press 1, to continue')
        gather.say('Or, press star, to hear your ID again')
    vr.say('We did not receive your selection')
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_id_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for register_id view"""
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)
    user_id = request.session.get('user_id', None)
    id_str = ', '.join(user_id)

    if selected_option == '1':  # continue to pin
        vr.say("You will use this ID, along with a short pin, to access your account.")
        vr.redirect(reverse('register-pin'))

    elif selected_option == '*':  # repeat ID and options
        with vr.gather(
        action=reverse('register-id-dig'),
        num_digits=1,
        timeout=5,
        ) as gather:
            gather.say(f"Please write down this ID, {id_str}")

            gather.say('Press 1, to continue')
            gather.pause()
            gather.say('Or, press star, to hear your ID again')
        vr.say('We did not receive your selection')
        vr.redirect(reverse('register-focus'))
    
    else:
        vr.say("Sorry, invalid option")
        vr.redirect(reverse('register-id'))
    
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_pin(request: HttpRequest) -> HttpResponse:
    """View for getting user's pin for their account"""
    vr = VoiceResponse()

    vr.say("For the last step, please come up with a 4 to 6 digit pin, and write it down.")
    vr.pause()
    with vr.gather(
        action=reverse('register-pin-confirm'),
        num_digits=6,
        finish_on_key='#',
        timeout=10,
    ) as gather:
        gather.say("When you are ready, enter the pin here, followed by the pound key.")
    vr.say('We did not receive your selection')
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_pin_confirm(request: HttpRequest) -> HttpResponse:
    """View for confirming user's pin (& handling no pin entry)"""
    vr = VoiceResponse()
    entered_pin = request.POST.get('Digits', None)

    if not entered_pin:
        vr.say("We did not receive a pin.") 
        vr.redirect(reverse('register-pin'))
    
    else:
        request.session['first_pin'] = entered_pin
        vr.say("Please confirm your pin by entering it again.")
        with vr.gather(
            action=reverse('register-pin-confirm-dig'),
            num_digits=6,
            finish_on_key='#',
            timeout=10,
        ) as gather:
            gather.say("Press the pound key once you are finished.")
        vr.say('We did not receive your selection')
        vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_pin_confirm_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for the confirming the pin"""
    vr = VoiceResponse()
    entered_pin = request.POST.get('Digits', None)
    user_id = request.session.get('user_id', None)
    first_pin = request.session.get('first_pin', None)

    if not entered_pin:
        vr.say("We did not receive a pin.") 
        vr.redirect(reverse('register-pin-confirm'))
    
    else:
        # Check if pins match
        if first_pin == entered_pin:
            register_IVRUser_final(user_id, entered_pin)
            request.session['auth'] = True
            del request.session["first_pin"]

            vr.say("You have finished registering.")
            vr.say("Please keep your user ID and pin in a safe place.")
            vr.pause()
            vr.say("We will now redirect you to the main menu")
            vr.redirect(reverse('main'))
        else:
            del request.session["first_pin"]
            vr.say("Sorry, your pins do not match. Let's try again.")
            vr.redirect(reverse('register-pin'))

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_name_process(request: HttpRequest) -> HttpResponse:
    call_sid = request.POST.get('CallSid', None)
    recording_sid = request.POST.get('RecordingSid', None)
    recording_url = request.POST.get('RecordingUrl', None)

    recording_status = request.POST.get('RecordingStatus', None)

    # TODO - test recording status being failed

    # Create TempRecording in DB
    temp_recording = TempRecording(call_sid=call_sid,
                                   recording_type=RecordingType.ACCOUNT_NAME,
                                   failed=(recording_status == 'failed'),
                                   recording_sid=recording_sid,
                                   recording_url=recording_url)
    temp_recording.save()

    return HttpResponse("", content_type='text/xml')
