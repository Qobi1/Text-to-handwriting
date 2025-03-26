from django.shortcuts import render, redirect
from .models import Contact
from .forms import ContactForm
from django.contrib import messages


def index(request):
    return render(request, 'main.html')


def main(request):
    return render(request, 'index.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Request is saved, we will contact u soon!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def about(request):
    return render(request, 'about.html')


def pricing(request):
    return render(request, 'pricing.html')
