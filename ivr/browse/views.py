# browse/views.py
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from browse.models import *
import os

## Global variables
CUR_URL = "https://cedbb33691f9.ngrok.io"

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


# TODO - store session values as strings if necessary

@csrf_exempt
def browse_content(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    base_index = request.session.get('browse_content_base_index', 0)
    vr = VoiceResponse()

    # print(selected_option)
    # print(base_index)

    # TODO - handle invalid entry here, to avoid unnecessary database load
    contents = (Title.objects.order_by('id').filter(id__isnull=False))

    # Show browse content menu (initial request)
    if selected_option is None:
        # Start getting user input at any point in the interaction
        with vr.gather(
                action=reverse('browse-content'),
                finish_on_key='#',
                timeout=10,
        ) as gather:

            # Say the appropriate header message
            if base_index == 0:
                gather.say('Welcome to the Browse Content Menu')
            if base_index < 0:
                gather.say('You are at the top of the content list')
                request.session['browse_content_base_index'] = 0
                base_index = 0
            elif base_index > 0:
                gather.say('Next three entries')

            # Say the menu options if top of list
            if base_index == 0:
                gather.say('Press the number, then # to select an entry')
                gather.pause()
                gather.say('1, 2, or 3 to select content to listen to')
                gather.pause()
                gather.say('4, to hear the previous three entries')
                gather.pause()
                gather.say('6, to hear the next three entries')
                # gather.say('Press 1, 2, or 3 then # to select an entry')
                # gather.pause()
                # gather.say('Press 4, then #, to hear the previous three entries')
                # gather.pause()
                # gather.say('Press 6, then #, to hear the next three entries')

            # Scroll through content list by base index
            # contents = (Title.objects.order_by('id').filter(id__isnull=False))
            gather.pause()
            contents = contents[base_index: base_index + 3]

            # Handle end of list
            if not contents:
                gather.say('No more entries left.')
                gather.pause()
                gather.say('Press 4, then #, to hear the previous three entries')
                gather.pause()
                gather.say('Press 7, then #, to return to the top of the list')

            # List the contents
            for count, content in enumerate(contents):
                gather.say('For ' + content.name + ', press '+ str(count + 1))
                gather.pause()
            
            # Remind user of scrolling options
            gather.pause(length=7)
            gather.say('Press the number, then # to select an entry')
            gather.pause()
            gather.say('1, 2, or 3 to select content to listen to')
            gather.pause()
            gather.say('4 to hear the previous three entries')
            gather.pause()
            gather.say('6 to hear the next three entries')
            if base_index > 0:
                gather.say('7 to return to the top of the list')

        vr.say('We did not receive your selection')
        vr.redirect('')
        return HttpResponse(str(vr), content_type='text/xml')

    # Handle option selection, scroll in browse content menu or redirect to listen
    else:
        # Continue scrolling in browse_content
        if selected_option in ['4', '6', '7']:
            if selected_option == '4':
                request.session['browse_content_base_index'] = base_index - 3
            if selected_option == '6':
                request.session['browse_content_base_index'] = base_index + 3
            if selected_option == '7':
                request.session['browse_content_base_index'] = 0

            vr.redirect(reverse('browse-content'))
            return HttpResponse(str(vr), content_type='text/xml')
        
        # Play a selected entry
        elif selected_option in ['1', '2', '3']:
            contents = contents[base_index: base_index + 3]
            content = contents[int(selected_option) - 1]
            request.session['listen_name'] = content.name
            request.session['listen_id'] = content.id
            request.session['listen_path'] = content.files
            vr.redirect(reverse('listen'))
            return HttpResponse(str(vr), content_type='text/xml')

        # Handle invalid option
        else:
            vr.say('Invalid Entry  ')
            vr.redirect(reverse('browse-content'))
            return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def listen(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    content_name = request.session.get('listen_name', '')
    content_id = request.session.get('listen_id', '')
    content_path = request.session.get('listen_path', '')
    
    # Redirect to same position in list if content name and path not set
    if not (content_name and content_id and content_path):
        vr.say("I'm sorry, there was an error on our end. Returning you to the browse content menu")
        vr.redirect(reverse('browse-content'))
        return HttpResponse(str(vr), content_type='text/xml')

    # Get list of files in this Title's folder
    audio_list = os.listdir(settings.MEDIA_ROOT + '/' + str(content_id))
    first_file = audio_list[0]

    file_url = CUR_URL + content_path + first_file
    # print(file_url)
    
    vr.say('Hello, you are listening to ' + content_name)
    vr.pause(1)
    vr.say('Please wait just a moment while the file is loaded')
    vr.play(file_url)
    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def request_content(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Welcome to the Make Request Menu')
    vr.say('Sorry, under construction')
    vr.redirect(reverse('welcome'))
    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def browse_requests(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Welcome to the Browse Requests Menu')
    vr.say('Sorry, under construction')
    vr.redirect(reverse('welcome'))
    return HttpResponse(str(vr), content_type='text/xml')
