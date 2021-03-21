# browse/views.py
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse

from .models import Content

@csrf_exempt
def welcome(request: HttpRequest) -> HttpResponse:
   vr = VoiceResponse()
   with vr.gather(
      num_digits=1, action=reverse('menu'), finish_on_key='#',
   ) as gather:
      gather.say(message="Welcome to the Main Menu.   " +
         "Please make a selection, then press #.  " +
         "Press 1 to browse content.   " +
         "Press 2 to request content.   " +
         "Press 3 to browse requests.   ", loop=3)
   
   vr.say('We did not receive your selection')
   vr.redirect('')

   return HttpResponse(str(vr), content_type='text/xml')


@csrf_exempt
def menu(request: HttpRequest) -> HttpResponse:
   
   selected_option = request.POST.get('Digits')
   option_actions = {'1': 'browse-content',
                     '2': 'request-content',
                     '3': 'browse-requests'}

   if selected_option in option_actions:
      vr = VoiceResponse()
      vr.redirect(reverse(option_actions[selected_option]))
      return HttpResponse(str(vr), content_type='text/xml')

   vr.redirect('welcome')
   return HttpResponse(str(vr), content_type='text/xml') 


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

   try:
      entry = Content.objects.get(id=digits)

   except Content.DoesNotExist:
      vr.say('Please select Content entries 1, 2, or 3.')
      vr.redirect(reverse('browse-content'))

   else:
      
      vr.say(f'{entry.body}')
      vr.say('Info message, End of Content, Returning to Browse Content Menu')
      vr.redirect(reverse('browse-content'))

      return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def browse_requests(request: HttpRequest) -> HttpResponse:
   vr = VoiceResponse()
   vr.say('Welcome to the Browse Requests Menu')

   vr.say('Sorry, under construction')
   vr.redirect('')

   return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def make_request(request: HttpRequest) -> HttpResponse:
   vr = VoiceResponse()
   vr.say('Welcome to the Make Request Menu')

   vr.say('Sorry, under construction')
   vr.redirect('')

   return HttpResponse(str(vr), content_type='text/xml')
