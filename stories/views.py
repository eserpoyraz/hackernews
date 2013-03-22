from django.http import HttpResponse

def index(request):
    return HttpResponse('Anasayfa buralar hep')
