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
        vr.say('Welcome to Be My Reader.')
        vr.pause()
        with vr.gather(
                action=reverse('welcome'),
                #finish_on_key='#',
                numDigits=1,
                timeout=1,
        ) as gather:
            gather.say('Press 1 to browse existing content.')
            gather.pause()
            gather.say('Press 2 to request new content.')
            gather.pause()
            gather.say('Press 3 to browse requests, or make a recording.')
            gather.pause()
            gather.say('Press star, to repeat these options.')
            gather.pause(length=5)
        vr.say('We did not receive your selection.')
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
