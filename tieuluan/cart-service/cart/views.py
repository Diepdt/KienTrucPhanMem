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


def get_product_info(product_id):
    """Get unified product info from product-service."""
    try:
        resp = http_requests.get(
            f"{django_settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/",
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"get_product_info error: {e}")
    return None


def _normalize_product_payload(payload):
    attributes = payload.get('attributes') if isinstance(payload.get('attributes'), dict) else {}
    category_payload = payload.get('category') if isinstance(payload.get('category'), dict) else {}

    subtitle_parts = [
        attributes.get('brand', ''),
        attributes.get('model', ''),
    ]
    subtitle = ' | '.join([part for part in subtitle_parts if part])

    return {
        'product_type': str(payload.get('product_type', '')).strip().lower(),
        'product_id': payload.get('id'),
        'product_name': payload.get('name', ''),
        'product_subtitle': subtitle,
        'product_image_url': payload.get('image_url', ''),
        'price': payload.get('price', 0),
        'stock': payload.get('stock', 0),
        'product_snapshot': {
            'category_id': category_payload.get('id'),
            'category_name': category_payload.get('name', ''),
            'description': payload.get('description', ''),
            'attributes': attributes,
        },
    }


def resolve_product_for_cart(request_data):
    """Resolve product info from standardized payload fields."""
    product_type = str(request_data.get('product_type', '')).strip().lower()
    product_id = request_data.get('product_id')

    if not product_type:
        return None, "product_type bắt buộc", 400

    if product_id is None:
        return None, "product_id bắt buộc", 400

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return None, "product_id phải là số nguyên", 400

    raw = get_product_info(product_id)
    if not raw:
        return None, "Sản phẩm không tồn tại hoặc không khả dụng", 404

    resolved_type = str(raw.get('product_type', '')).strip().lower()
    if resolved_type != product_type:
        return None, "product_type không khớp với sản phẩm", 400

    normalized = _normalize_product_payload(raw)
    normalized['source_service'] = 'product-service'
    return normalized, None, 200


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
    """Thêm sản phẩm vào giỏ hàng (đa loại: book/cloth/...)."""

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            return Response({'error': 'quantity không hợp lệ'}, status=400)
        if quantity < 1:
            return Response({'error': 'quantity phải lớn hơn 0'}, status=400)

        product, error_message, code = resolve_product_for_cart(request.data)
        if error_message:
            return Response({'error': error_message}, status=code)
        if product.get('stock', 0) < quantity:
            return Response({'error': 'Sản phẩm không đủ số lượng trong kho'}, status=400)

        cart, _ = Cart.objects.get_or_create(customer_id=customer['id'])
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=product['product_type'],
            product_id=product['product_id'],
            defaults={
                'product_name': product['product_name'],
                'product_subtitle': product['product_subtitle'],
                'product_image_url': product['product_image_url'],
                'source_service': product['source_service'],
                'product_snapshot': product['product_snapshot'],
                'price': product['price'],
                'quantity': quantity,
            }
        )
        if not created:
            if product.get('stock', 0) < (cart_item.quantity + quantity):
                return Response({'error': 'Sản phẩm không đủ số lượng trong kho'}, status=400)
            cart_item.product_name = product['product_name']
            cart_item.product_subtitle = product['product_subtitle']
            cart_item.product_image_url = product['product_image_url']
            cart_item.source_service = product['source_service']
            cart_item.product_snapshot = product['product_snapshot']
            cart_item.price = product['price']
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=200)


class UpdateCartItemView(APIView):
    """Cập nhật số lượng sản phẩm trong giỏ."""

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
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return Response({'error': 'quantity không hợp lệ'}, status=400)
            if quantity <= 0:
                item.delete()
                return Response({'message': 'Đã xóa sản phẩm khỏi giỏ hàng'})

            product_info = get_product_info(item.product_id)
            stock = int((product_info or {}).get('stock', 0))
            if stock < quantity:
                return Response({'error': 'Sản phẩm không đủ số lượng trong kho'}, status=400)

            product_type = str((product_info or {}).get('product_type', '')).strip().lower()
            if product_type and product_type != item.product_type:
                return Response({'error': 'product_type không còn hợp lệ cho sản phẩm này'}, status=400)

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
            item_ids = request.data.get('item_ids')
            if item_ids and isinstance(item_ids, list):
                cart.items.filter(id__in=item_ids).delete()
            else:
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


class AddToCartInternalView(APIView):
    """
    Thêm sách vào giỏ hàng (internal) – dành cho agent-service gọi.
    Không yêu cầu xác thực customer token; xác thực service-to-service
    được thực hiện bởi network layer (Docker internal network).

    POST /api/carts/add-internal/
        Body: { "customer_id": int, "product_id": int, "product_type": str, "quantity": int }
    """

    def post(self, request):
        customer_id = request.data.get('customer_id')
        quantity_raw = request.data.get('quantity', 1)
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            return Response({'error': 'quantity không hợp lệ'}, status=400)

        if not customer_id:
            return Response({'error': 'customer_id bắt buộc'}, status=400)
        if quantity < 1:
            return Response({'error': 'quantity phải lớn hơn 0'}, status=400)

        product, error_message, code = resolve_product_for_cart(request.data)
        if error_message:
            return Response({'error': error_message}, status=code)
        if product.get('stock', 0) < quantity:
            return Response({'error': 'Sản phẩm không đủ số lượng trong kho'}, status=400)

        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=product['product_type'],
            product_id=product['product_id'],
            defaults={
                'product_name': product['product_name'],
                'product_subtitle': product['product_subtitle'],
                'product_image_url': product['product_image_url'],
                'source_service': product['source_service'],
                'product_snapshot': product['product_snapshot'],
                'price': product['price'],
                'quantity': quantity,
            },
        )
        if not created:
            if product.get('stock', 0) < (cart_item.quantity + quantity):
                return Response({'error': 'Sản phẩm không đủ số lượng trong kho'}, status=400)
            cart_item.product_name = product['product_name']
            cart_item.product_subtitle = product['product_subtitle']
            cart_item.product_image_url = product['product_image_url']
            cart_item.source_service = product['source_service']
            cart_item.product_snapshot = product['product_snapshot']
            cart_item.price = product['price']
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=200)
