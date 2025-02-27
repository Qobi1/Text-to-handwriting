from django.shortcuts import render



def index(request):
    return render(request, 'index.html')


def image_to_text(request):
    return render(request, 'image_to_text.html')


def contact(request):
    return render(request, 'contact.html')