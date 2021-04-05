# browse/views.py
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from browse.models import *

## Global variables
index = 0
CUR_URL = "https://a211ee428d6c.ngrok.io"

@csrf_exempt
def welcome(request: HttpRequest) -> HttpResponse:

    vr = VoiceResponse()
    vr.say('Welcome to Be My Reader')
    print(request)
    with vr.gather(
            action=reverse('menu'),
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


@csrf_exempt
def menu(request: HttpRequest) -> HttpResponse:

    vr = VoiceResponse()
    vr.say('Standby while we route your connection')

    selected_option = request.POST.get('Digits')
    option_actions = {'1': 'browse-content',
                      '2': 'request-content',
                      '3': 'browse-requests'}

    if selected_option in option_actions:
      #vr = VoiceResponse()
        vr.redirect(reverse(option_actions[selected_option]))
        return HttpResponse(str(vr), content_type='text/xml')
    vr.say('Invalid Entry  ')
    vr.redirect(reverse('welcome'))
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def browse_content(request: HttpRequest) -> HttpResponse:
    file_path = str()
    vr = VoiceResponse()
    vr.say('Welcome to the Browse Content Menu')
    vr.say('Press 1, 2, or 3 then # to select an entry')
    vr.pause()
    vr.say('Press 4 to hear the previous three entries')
    vr.pause()
    vr.say('Press 6 to hear the next three entries')

    with vr.gather(
            action=reverse('listen'),
            finish_on_key='#',
            timeout=10,
    ) as gather:
       #gather.say('Please choose which content to listen to, then press #')
        contents = (Title.objects.order_by('id'))
            #.filter(id__isnull=False, id__gte=index+1, id__lte=index+3)

        for count, content in enumerate(contents):
            gather.say('For ' + str(content.name) + ' press '+ str(count))
    vr.say('We did not receive your selection')
    vr.redirect('')
    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def listen(request: HttpRequest) -> HttpResponse:
    """
    contents = (
        Title.objects
        .filter(id__isnull=False, id__gte=index+1, id__lte=index+3)
        .order_by('id')
    )
    """
    file_url = CUR_URL + settings.MEDIA_URL + request.GET.get('f', '')
    vr = VoiceResponse()
    vr.say('Hello, please wait just a moment while the file is loaded.')
    vr.play(file_url)
    return HttpResponse(str(vr), content_type='text/xml')

"""
@csrf_exempt
def listen_content(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Retrieving content   ')
    digits = request.POST.get('Digits')

    try:
        entry = Title.objects.get(id=int(digits)+index)
    except Title.DoesNotExist:
        vr.say('Invalid content.  ')
        vr.redirect(reverse('browse-content'))
    else:
        vr.say(f'{entry.body}')
        vr.say('Info message, End of Content, Returning to Browse Content Menu')
        vr.redirect(reverse('browse-content'))
    return HttpResponse(str(vr), content_type='text/xml')
"""

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
