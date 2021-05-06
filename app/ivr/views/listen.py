from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from ivr.models import *
import os


@csrf_exempt
def listen(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    #content_name = request.session.get('listen_name', '')
    content_id = request.session.get('listen_id', '')
    content_path = request.session.get('listen_path', '')
    file_no = request.session.get('file_no', '0')
    paused = request.session.get('paused', 'no')

    # Redirect to same position in list if content name and path not set
    if not (content_id and content_path):
        vr.say("I'm sorry, there was an error on our end. Returning you to the browse content menu")
        vr.redirect(reverse('browse-content'))
        return HttpResponse(str(vr), content_type='text/xml')
    if int(file_no) < 0:
        vr.say("can't go back further, you are at the beginning")
        request.session['file_no'] = '0'
        vr.redirect(reverse('listen'))

    with vr.gather(
        action=reverse('listen-dig'),
        numDigits=1,
        timeout=5,
    ) as gather:
    #vr.say('Hello, you are listening to ' + content_name)
    #vr.pause(1)
        audio_path = settings.MEDIA_ROOT + '/' + str(content_id)
        file_url = settings.CUR_URL + content_path + file_no + '.mp3'
        print(file_url)
        gather.say('Please wait a moment while the file is loaded, or press 9 to go back.')
        gather.play(file_url)
    return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def listen_dig(request: HttpRequest) -> HttpResponse:
    selected_option = request.POST.get('Digits', None)
    call_sid = request.POST.get('CallSid', None)
    paused = request.POST.get('paused', 'no')
    vr = VoiceResponse()

    if paused = 'yes' and not selected_option == None:
        request.session['paused'] = 'no'
    elif selected_option == '4':
        request.session['file_no'] = str(int(request.POST.get('file_no'))-1)
    elif selected_option == '6':
        request.session['file_no'] = str(int(request.POST.get('file_no'))+1)
    elif selected_option == '5':
        request.session['paused'] = 'yes'
    vr.redirect(reverse('listen'))
    return HttpResponse(str(vr), content_type='text/xml')
