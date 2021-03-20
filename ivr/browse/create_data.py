from browse.models import Content

Content.objects.create(head='Math', body='A plus B equals C', digits=1)
Content.objects.create(head="Shakespeare", body='To be or not to be', digits=2)
Content.objects.create(head="Science", body='Pluto is not a planet', digits=3)