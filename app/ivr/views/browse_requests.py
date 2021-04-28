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

@csrf_exempt
def browse_requests(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    base_index = request.session.get('browse_requests_base_index', 0)
    vr = VoiceResponse()

    # print(selected_option)
    # print(base_index)

    # TODO - handle invalid entry here, to avoid unnecessary database load
    requests = (Request.objects.order_by('id').filter(id__isnull=False))

    # Show browse request menu (initial request)
    if selected_option is None:
        # Start getting user input at any point in the interaction
        with vr.gather(
                action=reverse('browse-requests'),
                #finish_on_key='#',
                numDigits=1,
                timeout=1,
        ) as gather:

            # Say the appropriate header message
            if base_index == 0:
                gather.say('Welcome to the Browse Content Menu')
            if base_index < 0:
                gather.say('You are at the top of the request list')
                request.session['browse_requests_base_index'] = 0
                base_index = 0
            elif base_index > 0:
                gather.say('Next three entries')

            # Say the menu options if top of list
            if base_index == 0:
                gather.say('Press a number to navigate the list')
                gather.pause()
                for count, request in enumerate(requests):
                    gather.play(request.title_file.url)
                    gather.pause()
                gather.say('Press 4, to hear the previous three entries')
                gather.pause()
                gather.say('Press 6, to hear the next three entries')
                gather.pause()
                gather.say('Press 9, to return to the main menu')
                gather.pause()
                gather.say('Press Star, to repeat these options')
                gather.pause()

            # Scroll through request list by base index
            # requests = (Title.objects.order_by('id').filter(id__isnull=False))
            gather.pause()
            requests = requests[base_index: base_index + 3]

            # Handle end of list
            if not requests:
                gather.say('No more entries left.')
                gather.pause()
                gather.say('Press 4, to hear the previous three entries')
                gather.pause()
                gather.say('Press 7, to return to the top of the list')
                gather.pause()
                gather.say('Press 9, to return to the main menu')
                gather.pause()
                gather.say('Press star, to repeat these options')
                gather.pause()

            # Remind user of scrolling options
            gather.pause(length=7)
            for count, request in enumerate(requests):
                gather.play(request.title_file.url)
                gather.pause()
            gather.say('Press 4, to hear the previous three entries')
            gather.pause()
            gather.say('Press 6, to hear the next three entries')
            if base_index > 0:
                gather.pause()
                gather.say('Press 7, to return to the top of the list')
            gather.pause()
            gather.say('Press 9, to return to the main menu')
            gather.pause()
            gather.say('Press star, to repeat these options')
            gather.pause()

        vr.say('We did not receive your selection')
        vr.redirect('')
        return HttpResponse(str(vr), content_type='text/xml')

    # Handle option selection, scroll in browse requests menu or redirect to listen
    else:
        # Continue scrolling in browse_requests
        if selected_option in ['4', '6', '7']:
            if selected_option == '4':
                request.session['browse_requests_base_index'] = base_index - 3
            if selected_option == '6':
                request.session['browse_requests_base_index'] = base_index + 3
            if selected_option == '7':
                request.session['browse_requests_base_index'] = 0

            vr.redirect(reverse('browse-requests'))
            return HttpResponse(str(vr), content_type='text/xml')

        # Return to main menu
        elif selected_option == '9':
            vr.redirect(reverse('welcome'))
            return HttpResponse(str(vr), content_type='text/xml')

        # Repeat options at current position
        elif selected_option == '*':
            vr.redirect(reverse('browse-requests'))
            return HttpResponse(str(vr), content_type='text/xml')

        # Handle invalid option
        else:
            vr.say('Invalid Entry  ')
            vr.redirect(reverse('browse-requests'))
            return HttpResponse(str(vr), content_type='text/xml')
