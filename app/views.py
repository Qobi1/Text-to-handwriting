from django.shortcuts import render



def index(request):
    return render(request, 'main.html')


def main(request):
    return render(request, 'main.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


def pricing(request):
    return render(request, 'pricing.html')