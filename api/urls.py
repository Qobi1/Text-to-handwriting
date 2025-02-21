from django.urls import path
from .views import TextToHandwritingAPIView

urlpatterns = [
    path('text-to-handwriting/', TextToHandwritingAPIView.as_view(), name='text_to_handwriting')
]