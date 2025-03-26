import os
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, MultiPartParser
from api.serializers import TextToHandwritingSerializer, ConvertImageToPdfSerializer
from app.tasks import text_to_handwriting, convert_images_to_pdf
from celery.result import AsyncResult
from django.core.files.storage import default_storage
from text_to_handwritting.settings import BACKEND_URL


class TextToHandwritingAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser, MultiPartParser]
    serializer_class = TextToHandwritingSerializer

    @extend_schema(
        request=serializer_class,
        responses={201: serializer_class, 400: None},
        tags=['Text to handwriting']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        background_image = request.FILES.get("background_image", None)  # Get uploaded file
        if serializer.is_valid():
            validated_data = serializer.validated_data
            if background_image:
                # Save file to media/uploads/
                upload_dir = os.path.join(settings.MEDIA_ROOT, "uploaded_backgrounds")
                os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists

                file_path = os.path.join(upload_dir, background_image.name)
                with default_storage.open(file_path, "wb") as f:
                    for chunk in background_image.chunks():
                        f.write(chunk)
                validated_data["background_image"] = file_path
            task = text_to_handwriting.delay(**validated_data)
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
            # Ensure it's a single file path
            if isinstance(task_result.result, str) and task_result.result.endswith('pdf'):
                print(task_result.result)
                # Get the filename from the full file path
                filename = os.path.basename(task_result.result)
                print(filename)
                # Build the URL to access the file via Django
                image_urls = request.build_absolute_uri(settings.MEDIA_URL + filename)
            else:
                # Convert file paths to URLs
                image_urls = task_result.result  # List of local file paths

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
