from django.urls import path
from .views import index, main, contact, about, pricing

urlpatterns = [
    path('', index, name='index'),
    path('main/', main, name='main'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('pricing/', pricing, name='pricing'),
]
