from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import *
import os


# TODO - make file listing all session variables for call + specific menus
# TODO - check & store CallSid upon entry to welcome, flush session as appropriate


@csrf_exempt
def welcome(request: HttpRequest) -> HttpResponse:
    """View welcoming to BeMyReader and presenting login/registration/guest options"""
    vr = VoiceResponse()
    post_call_sid = request.POST.get('CallSid', None)
    post_phone_number = request.POST.get('From', None)
    session_call_sid = request.session.get('call_sid', None)

    # Session should never be set at call start (but could be if returning from repeat, login, register)
    # NOTE - might want to remove
    if session_call_sid is not None:
        if session_call_sid != post_call_sid:
            print("WARNING: POST CallSid not equal to session call_sid")
            request.session.flush()
    
    # Handle session initialization
    request.session['call_sid'] = post_call_sid
    request.session['phone_number'] = post_phone_number

    # Present welcome message
    # TODO - improve this message (Ben and/or Tim)!!!
    vr.say("Welcome to BeMyReader, a free platform to share audio recordings of texts, for the visually impaired.")
    
    # TODO - might want to bind "learn more" to the help key for consistency
    # -- would then bind log in, register, and guest to 1, 2, 3, respectively
    with vr.gather(
                action=reverse('welcome-dig'),
                #finish_on_key='#',
                numDigits=1,
                timeout=5,
        ) as gather:
            gather.say('Please select one of the following options')
            gather.pause()
            gather.say('Press 1, to learn more about this service')
            gather.pause()
            gather.say('Press 2, to log in')
            gather.pause()
            gather.say('Press 3, to register')
            gather.pause()
            gather.say('Press 4, to continue as a guest')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
    vr.say('We did not receive your selection')
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def welcome_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for welcome view"""
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)

    if selected_option == '1':  # learn more selected
        vr.redirect(reverse('learn-more'))
    
    elif selected_option == '2':  # log in selected
        vr.redirect(reverse('login-id'))

    elif selected_option == '3':  # register selected
        vr.redirect(reverse('register-start'))
    
    elif selected_option == '4':  # continue as guest selected
        vr.say('Okay, continuing as a guest')
        vr.redirect(reverse('main'))
    
    elif selected_option == '*':  # repeat selected
        with vr.gather(
                action=reverse('welcome-dig'),
                #finish_on_key='#',
                numDigits=1,
                timeout=5,
        ) as gather:
            gather.say('Please select one of the following options')
            gather.pause()
            gather.say('Press 1, to learn more about this service')
            gather.pause()
            gather.say('Press 2, to log in')
            gather.pause()
            gather.say('Press 3, to register')
            gather.pause()
            gather.say('Press 4, to continue as a guest')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
        vr.say('We did not receive your selection')
        vr.redirect(reverse('welcome'))
    
    else:
        vr.say("Sorry, invalid option")
        vr.redirect(reverse('welcome'))
    
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
# TODO - BEN AND/OR TIM PLEASE IMPLEMENT LEARN_MORE
def learn_more(request: HttpRequest) -> HttpResponse:
    """View describing BeMyReader in greater detail"""
    vr = VoiceResponse()
    vr.say("Not yet implemented")
    vr.hangup()
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
# TODO - Michael, finish implementing
def login_id(request: HttpRequest) -> HttpResponse:
    """View for logging in to an existing account"""
    vr = VoiceResponse()
    vr.say("Not yet implemented")
    vr.hangup()
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def register_start(request: HttpRequest) -> HttpResponse:
    """View for logging in to an existing account"""
    vr = VoiceResponse()
    vr.say('Creating a BeMyReader account will allow you to request content, '
            'record content, and more.')
    vr.pause()
    vr.say('However, you can also browse and listen to existing content without an account')
    vr.pause()
    with vr.gather(
                action=reverse('register-start-dig'),
                #finish_on_key='#',
                numDigits=1,
                timeout=5,
        ) as gather:
            gather.say('How would you like to proceed?')
            gather.pause()
            gather.say('Press 1, to continue creating an account')
            gather.pause()
            gather.say('Press 9, to return to the welcome menu')
            gather.pause()
            gather.say('Or, press star, to repeat these options')
    vr.say('We did not receive your selection')
    vr.redirect(reverse('register-start'))


@csrf_exempt
def register_start_dig(request: HttpRequest) -> HttpResponse:
    """Processing digit entry for register_start view"""
    vr = VoiceResponse()
    selected_option = request.POST.get('Digits', None)

    if selected_option == '1':  # proceed with registration
        vr.redirect(reverse('register-focus'))
    
    elif selected_option == '9':  # return to welcome menu
        vr.redirect(reverse('welcome'))

    elif selected_option == '*':  # repeat selected
        with vr.gather(
                action=reverse('register-start-dig'),
                #finish_on_key='#',
                numDigits=1,
                timeout=5,
        ) as gather:
            gather.say('How would you like to proceed?')
            gather.pause()
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
def main(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    source_number = request.POST.get('From', None)
    source_country = request.POST.get('FromCountry', None)

    # Handle initial request to welcome
    # TODO - don't reset all session keys if returning to main menu
    if selected_option is None:
        # Clear session
        # TODO - improve this later
        request.session.flush()

        # TODO - remove after testing
        request.session['CallSid'] = request.POST.get('CallSid', None)

        vr = VoiceResponse()
        vr.say('Welcome to Be My Reader')
        with vr.gather(
                action=reverse('welcome'),
                #finish_on_key='#',
                numDigits=1,
                timeout=1,
        ) as gather:
            gather.say('Press the number to select an entry')
            gather.pause()
            gather.say('1 to browse content')
            gather.pause()
            gather.say('2 to request content')
            gather.pause()
            gather.say('3 to browse requests')
            gather.pause()
            gather.say('Star, to repeat these options')
            gather.pause(length=5)
        vr.say('We did not receive your selection')
        vr.redirect('')
        return HttpResponse(str(vr), content_type='text/xml')

    # Handle option selection, redirect to appropriate menu
    else:
        vr = VoiceResponse()
        option_actions = {'1': 'browse-content',
                        '2': 'request-menu',
                        '3': 'browse-requests',
                        '*': 'welcome'}
        if selected_option in option_actions:
            vr.redirect(reverse(option_actions[selected_option]))
            return HttpResponse(str(vr), content_type='text/xml')
        vr.say('Invalid Entry  ')
        vr.redirect(reverse('welcome'))
        return HttpResponse(str(vr), content_type='text/xml')