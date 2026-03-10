from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

logger = logging.getLogger(__name__)


def verify_customer_token(auth_header):
    """Xác thực customer token qua customer-service."""
    try:
        resp = http_requests.get(
            f"{django_settings.CUSTOMER_SERVICE_URL}/api/customers/verify-token/",
            headers={'Authorization': auth_header},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('valid', False), data.get('customer')
    except Exception as e:
        logger.error(f"verify_customer_token error: {e}")
    return False, None


def get_book_info(book_id):
    """Lấy thông tin sách từ book-service."""
    try:
        resp = http_requests.get(
            f"{django_settings.BOOK_SERVICE_URL}/api/books/{book_id}/",
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"get_book_info error: {e}")
    return None


class CreateCartView(APIView):
    """Tạo giỏ hàng - được gọi tự động bởi customer-service khi đăng ký."""

    def post(self, request):
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id bắt buộc'}, status=400)
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(CartSerializer(cart).data, status=201 if created else 200)


class GetCartView(APIView):
    """Xem giỏ hàng của khách hàng."""

    def get(self, request, customer_id):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid or customer['id'] != customer_id:
            return Response({'error': 'Unauthorized'}, status=401)
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response({'error': 'Giỏ hàng không tồn tại'}, status=404)


class AddToCartView(APIView):
    """Thêm sách vào giỏ hàng."""

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))

        if not book_id:
            return Response({'error': 'book_id bắt buộc'}, status=400)

        # Kiểm tra sách có tồn tại và còn hàng không
        book = get_book_info(book_id)
        if not book:
            return Response({'error': 'Sách không tồn tại'}, status=404)
        if book.get('stock', 0) < quantity:
            return Response({'error': 'Sách không đủ số lượng trong kho'}, status=400)

        cart, _ = Cart.objects.get_or_create(customer_id=customer['id'])
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={
                'book_title': book['title'],
                'book_author': book['author'],
                'price': book['price'],
                'quantity': quantity,
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=200)


class UpdateCartItemView(APIView):
    """Cập nhật số lượng sách trong giỏ."""

    def put(self, request, item_id):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        try:
            item = CartItem.objects.get(pk=item_id, cart__customer_id=customer['id'])
        except CartItem.DoesNotExist:
            return Response({'error': 'Không tìm thấy sản phẩm trong giỏ'}, status=404)

        quantity = request.data.get('quantity')
        if quantity is not None:
            quantity = int(quantity)
            if quantity <= 0:
                item.delete()
                return Response({'message': 'Đã xóa sản phẩm khỏi giỏ hàng'})
            item.quantity = quantity
            item.save()
        return Response(CartItemSerializer(item).data)


class RemoveFromCartView(APIView):
    """Xóa sách khỏi giỏ hàng."""

    def delete(self, request, item_id):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        try:
            item = CartItem.objects.get(pk=item_id, cart__customer_id=customer['id'])
            item.delete()
            return Response({'message': 'Đã xóa sản phẩm khỏi giỏ hàng'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Không tìm thấy sản phẩm trong giỏ'}, status=404)


class ClearCartView(APIView):
    """Xóa toàn bộ giỏ hàng - gọi từ order-service sau khi đặt hàng thành công."""

    def post(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            cart.items.all().delete()
            return Response({'message': 'Giỏ hàng đã được xóa sạch'})
        except Cart.DoesNotExist:
            return Response({'error': 'Không tìm thấy giỏ hàng'}, status=404)


class GetCartByCustomerInternalView(APIView):
    """Lấy giỏ hàng nội bộ - dành cho order-service gọi (không cần auth customer)."""

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response({'error': 'Giỏ hàng không tồn tại'}, status=404)
