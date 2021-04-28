"""Login interface: view presentation and entry handling functions, callbacks"""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import UserFocus, IVRUser
from ivr.logic.user import check_IVRUser_auth


@csrf_exempt
def login_id(request: HttpRequest) -> HttpResponse:
    """View for getting user's id for logging into their account"""
    vr = VoiceResponse()

    with vr.gather(
        action=reverse('login-id-check'),
        num_digits=6,
        finish_on_key='#',
        timeout=10,
    ) as gather:
        gather.say("To log in, please enter your user ID, followed by the pound key")
        gather.say("To cancel and return to the main menu, just press the pound key")
    vr.say('Log in cancelled')
    vr.redirect('welcome')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def login_id_check(request: HttpRequest) -> HttpResponse:
    """View for checking user ID (& handling no ID entry)"""
    vr = VoiceResponse()
    entered_id = request.POST.get('Digits', None).strip()
    print(f"login id: {entered_id}")

    if not entered_id:
        vr.say('Log in cancelled')
        vr.redirect(reverse('welcome'))
    else:
        request.session['login_id'] = entered_id
        vr.redirect('login-pin')

    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def login_pin(request: HttpRequest) -> HttpResponse:
    """View for getting user's pin for logging into their account"""
    vr = VoiceResponse()

    with vr.gather(
        action=reverse('login-pin-check'),
        num_digits=6,
        finish_on_key='#',
        timeout=10,
    ) as gather:
        gather.say("Please enter your pin, followed by the pound key")
        gather.say("To cancel and return to the main menu, just press the pound key")
    vr.say('Log in cancelled')
    vr.redirect('welcome')
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def login_pin_check(request: HttpRequest) -> HttpResponse:
    """View for checking user pin (& handling no pin entry)"""
    vr = VoiceResponse()
    entered_pin = request.POST.get('Digits', None).strip()
    entered_id = request.session.get('login_id', None)
    print(f"login pin: {entered_pin}")

    if not entered_pin:
        vr.say('Log in cancelled')
        vr.redirect(reverse('welcome'))
    else:
        auth = check_IVRUser_auth(entered_id, entered_pin)
        del request.session['login_id']
        if auth:
            request.session['user_id'] = entered_id
            request.session['auth'] = True
            vr.say("You are now logged in")
            vr.pause()
            vr.say("Going to the main menu")
            vr.redirect('main')
        else:
            vr.say("Sorry, your ID or pin were not correct")
            vr.pause()
            vr.say("Returning to the welcome menu")
            vr.redirect('welcome')

    return HttpResponse(str(vr), content_type='text/xml')