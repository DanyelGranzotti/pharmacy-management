from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from ..models.product import Product
from ..models.bank_account import BankAccount
from ..models.user import User
from ..serializers.transaction import PurchaseSerializer

class PurchaseProductView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Purchase a product",
        request_body=PurchaseSerializer,
        responses={
            200: 'Purchase successful',
            400: 'Bad Request',
            404: 'Product not found',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PurchaseSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            user = request.user

            try:
                product = Product.objects.get(id=product_id)
                total_cost = product.price * quantity

                bank_account = BankAccount.objects.get(user=user)
                if bank_account.balance >= total_cost:
                    bank_account.balance -= total_cost
                    bank_account.save()

                    user.purchased_products.add(product, through_defaults={'quantity': quantity})
                    return Response({'detail': 'Purchase successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            except BankAccount.DoesNotExist:
                return Response({'detail': 'Bank account not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)