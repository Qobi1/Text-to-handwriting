from django.urls import path
from .views import TextToHandwritingAPIView, TaskStatusView

urlpatterns = [
    path('text-to-handwriting/', TextToHandwritingAPIView.as_view(), name='text_to_handwriting'),
    path("api/task-status/<str:task_id>/", TaskStatusView.as_view(), name="task_status"),
]