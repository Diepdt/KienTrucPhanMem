from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Customer, CustomerToken
from .serializers import CustomerSerializer, CustomerRegisterSerializer, LoginSerializer

logger = logging.getLogger(__name__)


def get_customer_from_token(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    key = auth.split(' ', 1)[1]
    try:
        token = CustomerToken.objects.get(key=key)
        return token.customer if token.customer.is_active else None
    except CustomerToken.DoesNotExist:
        return None


def create_cart_for_customer(customer_id):
    """Gọi cart-service để tạo giỏ hàng cho khách hàng mới."""
    try:
        cart_url = django_settings.CART_SERVICE_URL
        resp = http_requests.post(
            f"{cart_url}/api/carts/create/",
            json={'customer_id': customer_id},
            timeout=5
        )
        if resp.status_code == 201:
            logger.info(f"Cart created for customer {customer_id}")
        else:
            logger.warning(f"Failed to create cart for customer {customer_id}: {resp.text}")
    except Exception as e:
        logger.error(f"Error creating cart for customer {customer_id}: {e}")


def verify_manager_token(auth_header):
    """Xác thực manager token để phục vụ tác vụ quản trị user."""
    try:
        resp = http_requests.get(
            f"{django_settings.MANAGER_SERVICE_URL}/api/manager/verify-token/",
            headers={'Authorization': auth_header},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('valid', False), data.get('manager')
    except Exception as e:
        logger.error(f"verify_manager_token error: {e}")
    return False, None


class RegisterView(APIView):
    """Đăng ký khách hàng - tự động tạo giỏ hàng."""

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        customer = serializer.save()
        # Tự động tạo giỏ hàng khi đăng ký thành công
        create_cart_for_customer(customer.id)
        token = CustomerToken.objects.create(
            customer=customer,
            key=CustomerToken.generate_key()
        )
        return Response({
            'message': 'Đăng ký thành công. Giỏ hàng đã được tạo tự động.',
            'token': token.key,
            'customer': CustomerSerializer(customer).data
        }, status=201)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=401)
        if not customer.check_password(password):
            return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=401)
        if not customer.is_active:
            return Response({'error': 'Tài khoản hiện đang bị cấm'}, status=401)
        token, _ = CustomerToken.objects.get_or_create(
            customer=customer, defaults={'key': CustomerToken.generate_key()})
        return Response({'token': token.key, 'customer': CustomerSerializer(customer).data})


class LogoutView(APIView):
    def post(self, request):
        customer = get_customer_from_token(request)
        if not customer:
            return Response({'error': 'Unauthorized'}, status=401)
        CustomerToken.objects.filter(customer=customer).delete()
        return Response({'message': 'Đăng xuất thành công'})


class CustomerDetailView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(pk=customer_id, is_active=True)
            return Response(CustomerSerializer(customer).data)
        except Customer.DoesNotExist:
            return Response({'error': 'Không tìm thấy khách hàng'}, status=404)

    def put(self, request, customer_id):
        customer = get_customer_from_token(request)
        if not customer or customer.id != customer_id:
            return Response({'error': 'Unauthorized'}, status=401)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class VerifyTokenView(APIView):
    """Xác thực customer token - gọi từ các service khác."""
    def get(self, request):
        customer = get_customer_from_token(request)
        if not customer:
            return Response({'valid': False}, status=401)
        return Response({'valid': True, 'customer': CustomerSerializer(customer).data})


class CustomerListView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        return Response(CustomerSerializer(customers, many=True).data)


class AdminCustomerStatusView(APIView):
    """Manager bật/tắt trạng thái hoạt động customer (ban/unban)."""

    def patch(self, request, customer_id):
        auth = request.headers.get('Authorization', '')
        valid, _manager = verify_manager_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        is_active = request.data.get('is_active', None)
        if is_active is None:
            return Response({'error': 'is_active là bắt buộc'}, status=400)

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Không tìm thấy khách hàng'}, status=404)

        customer.is_active = bool(is_active)
        customer.save(update_fields=['is_active'])
        return Response(CustomerSerializer(customer).data)
