import os

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.serializers import TextToHandwritingSerializer, ConvertImageToPdfSerializer
from app.tasks import text_to_handwriting, convert_images_to_pdf
from celery.result import AsyncResult

class TextToHandwritingAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    serializer_class = TextToHandwritingSerializer

    @extend_schema(
        request=serializer_class,
        responses={201: serializer_class, 400: None},
        tags=['Text to handwriting']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print(request.data)
        if serializer.is_valid():
            task = text_to_handwriting.delay(**serializer.data)
            return Response({"Response": task.id}, status=HTTP_200_OK, content_type='application/json')
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST, content_type='application/json')


class TaskStatusView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Get Celery Task Status",
        description="Retrieve the status of a Celery task by task_id. If completed, returns the PDF path.",
        parameters=[
            OpenApiParameter(
                name="task_id",
                description="Unique ID of the Celery task",
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {
                "description": "Task is either completed, pending, or in progress.",
                "examples": [
                    {"status": "completed", "pdf_path": "/media/generated_handwriting.pdf"},
                    {"status": "PENDING"},
                    {"status": "PROGRESS"}
                ]
            },
            400: {
                "description": "Task failed due to an error.",
                "examples": [{"status": "failed", "error": "Some error message"}]
            }
        },
    )
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        if task_result.state == "SUCCESS":
            # Convert file paths to URLs
            pdf_paths = task_result.result  # List of local file paths
            media_url = request.build_absolute_uri(settings.MEDIA_URL)  # Base media URL

            image_urls = [
                media_url + os.path.basename(path) for path in pdf_paths
            ]

            return Response({"status": "completed", "path": image_urls}, status=HTTP_200_OK)
        elif task_result.state == "FAILURE":
            return Response({"status": "failed", "error": str(task_result.info)}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": task_result.state}, status=HTTP_200_OK)


class ConvertImageToPdfAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    serializer_class = ConvertImageToPdfSerializer

    @extend_schema(
        request=serializer_class,
        responses={201: serializer_class, 400: None},
        tags=['Image to PDF']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            path = convert_images_to_pdf(**serializer.data)
            return Response({"Response": path}, status=HTTP_201_CREATED, content_type='application/json')
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST, content_type='application/json')
