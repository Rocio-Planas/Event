from django.http import HttpResponse

def home(request):
    return HttpResponse("Página de registro de tickets")