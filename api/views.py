from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.serializers import TextToHandwritingSerializer
from app.utils import text_to_handwriting


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
        if serializer.is_valid():
            response = text_to_handwriting(**serializer.data)
            return Response({"Response": response}, status=HTTP_200_OK, content_type='application/json')
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST, content_type='application/json')
