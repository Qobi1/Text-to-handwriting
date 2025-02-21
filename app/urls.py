from django.urls import path
from .views import index, image_to_text

urlpatterns = [
    path('', index, name='index'),
    path('image-extractor/', image_to_text, name='image_to_text')
]
