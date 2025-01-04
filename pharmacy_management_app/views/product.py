import csv
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models.product import Product
from ..serializers.product import ProductSerializer
from ..permissions import IsAdminUser

class ProductCSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Upload a CSV file with a list of products",
        manual_parameters=[
            openapi.Parameter(
                'file', openapi.IN_FORM, description="CSV file", type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={
            201: openapi.Response('Products uploaded successfully'),
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            products = []
            for row in reader:
                serializer = ProductSerializer(data=row)
                if serializer.is_valid():
                    products.append(serializer.save())
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Products uploaded successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)