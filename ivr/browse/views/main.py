from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from browse.models import *
import os


@csrf_exempt
def welcome(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)

    # Handle initial request to welcome
    if selected_option is None:
        # Clear session
        # TODO - improve this later
        request.session.flush()

        vr = VoiceResponse()
        vr.say('Welcome to Be My Reader')
        with vr.gather(
                action=reverse('welcome'),
                finish_on_key='#',
                timeout=10,
        ) as gather:
            gather.say('Press the number, then # to select an entry')
            gather.pause()
            gather.say('1 to browse content')
            gather.pause()
            gather.say('2 to request content')
            gather.pause()
            gather.say('3 to record content')
            gather.pause(length=5)
        vr.say('We did not receive your selection')
        vr.redirect('')
        return HttpResponse(str(vr), content_type='text/xml')

    # Handle option selection, redirect to appropriate menu
    else:
        vr = VoiceResponse()
        option_actions = {'1': 'browse-content',
                        '2': 'request-content',
                        '3': 'browse-requests'}
        if selected_option in option_actions:
            vr.redirect(reverse(option_actions[selected_option]))
            return HttpResponse(str(vr), content_type='text/xml')
        vr.say('Invalid Entry  ')
        vr.redirect(reverse('welcome'))
        return HttpResponse(str(vr), content_type='text/xml')