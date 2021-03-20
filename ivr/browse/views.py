# browse/views.py
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse

from .models import Content

@csrf_exempt
def browse_content(request: HttpRequest) -> HttpResponse:
   vr = VoiceResponse()
   vr.say('Welcome to the Browse Content Menu')

   with vr.gather(
       action=reverse('listen-content'),
       finish_on_key='#',
       timeout=20,
   ) as gather:
       gather.say('Please choose which content to listen to, then press #')
       contents = (
           Content.objects
           .filter(digits__isnull=False) # Todo: Filter for only the three entries to use
           .order_by('digits')
       )
       for content in contents:
           gather.say(f'For {content.head} press {content.digits}')

   vr.say('We did not receive your selection')
   vr.redirect('')

   return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def listen_content(request: HttpRequest) -> HttpResponse:
   vr = VoiceResponse()

   digits = request.POST.get('Digits')
   entry = Content.objects.get(id=request.GET['content'])

   try:
      content = Content.objects.get(digits=digits)

   except Content.DoesNotExist:
      vr.say('Please select Content entries 1, 2, or 3.')
      vr.redirect(reverse('browse-content'))

   else:
      vr.say('{entry.body}')
      vr.redirect(reverse('browse-content'))

      return HttpResponse(str(vr), content_type='text/xml')
