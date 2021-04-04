from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from django.conf import settings
from django.conf.urls.static import static
from browse.models import *
#from django.contrib.sites.models import get_current_site

#file_url = "https://4f704a9cb4be.ngrok.io/media/Count%20Zero%2001.mp3"

@csrf_exempt
def answer(request: HttpRequest) -> HttpResponse:
    """
    contents = (
        Title.objects
        .filter(id__isnull=False, id__gte=index+1, id__lte=index+3)
        .order_by('id')
    )
    """
    file_url = get_current_site(request) + settings.MEDIA_URL + request.GET.get('f', '')
    vr = VoiceResponse()
    vr.say('Hello, please wait just a moment while the file is loaded.')
    vr.play(file_url)
    return HttpResponse(str(vr), content_type='text/xml')
