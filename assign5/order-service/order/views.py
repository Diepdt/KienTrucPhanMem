from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as django_settings
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import requests as http_requests
import logging

from .models import Order, OrderItem
from .serializers import OrderSerializer

logger = logging.getLogger(__name__)


def verify_customer_token(auth_header):
    try:
        resp = http_requests.get(
            f"{django_settings.CUSTOMER_SERVICE_URL}/api/customers/verify-token/",
            headers={'Authorization': auth_header}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return d.get('valid', False), d.get('customer')
    except Exception as e:
        logger.error(f"verify_customer error: {e}")
    return False, None


def verify_manager_token(auth_header):
    try:
        resp = http_requests.get(
            f"{django_settings.MANAGER_SERVICE_URL}/api/manager/verify-token/",
            headers={'Authorization': auth_header}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('valid', False), data.get('manager')
    except Exception as e:
        logger.error(f"verify_manager error: {e}")
    return False, None


def get_cart_internal(customer_id):
    try:
        resp = http_requests.get(
            f"{django_settings.CART_SERVICE_URL}/api/carts/{customer_id}/internal/",
            timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"get_cart_internal error: {e}")
    return None


def get_shipping_method(method_id):
    try:
        resp = http_requests.get(
            f"{django_settings.SHIP_SERVICE_URL}/api/shipping/methods/{method_id}/",
            timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"get_shipping_method error: {e}")
    return None


def get_payment_method(method_id):
    try:
        resp = http_requests.get(
            f"{django_settings.PAY_SERVICE_URL}/api/payment/methods/{method_id}/",
            timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"get_payment_method error: {e}")
    return None


def create_payment(order_id, payment_method_id, amount):
    try:
        resp = http_requests.post(
            f"{django_settings.PAY_SERVICE_URL}/api/payment/create/",
            json={'order_id': order_id, 'payment_method_id': payment_method_id, 'amount': str(amount)},
            timeout=5)
        return resp.json() if resp.status_code == 201 else None
    except Exception as e:
        logger.error(f"create_payment error: {e}")
    return None


def create_shipment(order_id, shipping_method_id, address):
    try:
        resp = http_requests.post(
            f"{django_settings.SHIP_SERVICE_URL}/api/shipping/create/",
            json={'order_id': order_id, 'shipping_method_id': shipping_method_id,
                  'shipping_address': address},
            timeout=5)
        return resp.json() if resp.status_code == 201 else None
    except Exception as e:
        logger.error(f"create_shipment error: {e}")
    return None


def update_book_stock(items):
    try:
        payload = [{'book_id': item['book_id'], 'quantity': item['quantity']} for item in items]
        resp = http_requests.post(
            f"{django_settings.BOOK_SERVICE_URL}/api/books/update-stock/",
            json={'items': payload}, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"update_book_stock error: {e}")
    return False


def clear_cart(customer_id):
    try:
        http_requests.post(
            f"{django_settings.CART_SERVICE_URL}/api/carts/{customer_id}/clear/",
            timeout=5)
    except Exception as e:
        logger.error(f"clear_cart error: {e}")


class CreateOrderView(APIView):
    """
    Đặt hàng - kích hoạt thanh toán và vận chuyển.
    Body: { shipping_method_id, payment_method_id, shipping_address, notes }
    """

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        shipping_method_id = request.data.get('shipping_method_id')
        payment_method_id = request.data.get('payment_method_id')
        shipping_address = request.data.get('shipping_address', '')
        notes = request.data.get('notes', '')

        if not all([shipping_method_id, payment_method_id, shipping_address]):
            return Response({'error': 'shipping_method_id, payment_method_id, shipping_address bắt buộc'}, status=400)

        # 1. Lấy giỏ hàng
        cart = get_cart_internal(customer['id'])
        if not cart or not cart.get('items'):
            return Response({'error': 'Giỏ hàng trống, không thể đặt hàng'}, status=400)

        # 2. Lấy thông tin phương thức vận chuyển và thanh toán
        ship_method = get_shipping_method(shipping_method_id)
        pay_method = get_payment_method(payment_method_id)

        ship_cost = float(ship_method['cost']) if ship_method else 0.0
        ship_name = ship_method['name'] if ship_method else ''
        pay_name = pay_method['name'] if pay_method else ''

        # 3. Tính tổng tiền
        subtotal = float(cart['total'])
        total = subtotal + ship_cost

        # 4. Tạo đơn hàng
        order = Order.objects.create(
            customer_id=customer['id'],
            shipping_method_id=shipping_method_id,
            shipping_method_name=ship_name,
            shipping_cost=ship_cost,
            payment_method_id=payment_method_id,
            payment_method_name=pay_name,
            subtotal=subtotal,
            total_amount=total,
            shipping_address=shipping_address,
            notes=notes
        )

        # 5. Tạo order items từ cart
        for item in cart['items']:
            OrderItem.objects.create(
                order=order,
                book_id=item['book_id'],
                book_title=item['book_title'],
                book_author=item.get('book_author', ''),
                price=item['price'],
                quantity=item['quantity']
            )

        # 6. Kích hoạt thanh toán
        payment = create_payment(order.id, payment_method_id, total)
        if not payment:
            logger.warning(f"Payment creation failed for order {order.id}")

        # 7. Kích hoạt vận chuyển
        shipment = create_shipment(order.id, shipping_method_id, shipping_address)
        if not shipment:
            logger.warning(f"Shipment creation failed for order {order.id}")

        # 8. Cập nhật tồn kho sách
        update_book_stock(cart['items'])

        # 9. Xóa giỏ hàng
        clear_cart(customer['id'])

        return Response({
            'order': OrderSerializer(order).data,
            'payment': payment,
            'shipment': shipment,
        }, status=201)


class OrderListView(APIView):
    """Danh sách đơn hàng của khách hàng."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)
        orders = Order.objects.filter(customer_id=customer['id']).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)


class OrderHistoryView(APIView):
    """Lịch sử đơn hàng của khách hàng (alias rõ nghĩa cho frontend)."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)
        orders = Order.objects.filter(customer_id=customer['id']).order_by('-created_at')
        return Response({
            'count': orders.count(),
            'results': OrderSerializer(orders, many=True).data
        })


class CustomerOrdersInternalView(APIView):
    """Lấy đơn hàng của khách hàng - nội bộ (không cần auth, dành cho recommender)."""

    def get(self, request, customer_id):
        orders = Order.objects.filter(customer_id=customer_id).prefetch_related('items')
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    """Chi tiết đơn hàng."""

    def get(self, request, order_id):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)
        try:
            order = Order.objects.get(pk=order_id, customer_id=customer['id'])
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)

    def patch(self, request, order_id):
        """Hủy đơn hàng."""
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)
        try:
            order = Order.objects.get(pk=order_id, customer_id=customer['id'])
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)
        if order.status not in ('pending', 'confirmed'):
            return Response({'error': 'Không thể hủy đơn hàng ở trạng thái này'}, status=400)
        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)


class AdminOrderListView(APIView):
    """Danh sách đơn hàng cho manager/admin."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, manager = verify_manager_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        sort_by = request.query_params.get('sort_by', 'created_at')
        order_dir = request.query_params.get('order', 'desc').lower()

        sort_field_map = {
            'created_at': 'created_at',
            'total_amount': 'total_amount',
        }
        sort_field = sort_field_map.get(sort_by, 'created_at')
        if order_dir == 'asc':
            ordering = sort_field
        else:
            ordering = f"-{sort_field}"

        orders = Order.objects.all().prefetch_related('items').order_by(ordering)

        return Response({
            'actor': {'id': manager.get('id'), 'role': 'manager'},
            'sort': {'sort_by': sort_field, 'order': 'asc' if order_dir == 'asc' else 'desc'},
            'count': orders.count(),
            'results': OrderSerializer(orders, many=True).data,
        })


class AdminOrderDetailView(APIView):
    """Chi tiết/cập nhật trạng thái đơn hàng cho manager/admin."""

    ALLOWED_STATUS = {'pending', 'confirmed', 'shipping', 'delivered'}

    def get(self, request, order_id):
        auth = request.headers.get('Authorization', '')
        valid, _manager = verify_manager_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        try:
            order = Order.objects.prefetch_related('items').get(pk=order_id)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)

    def patch(self, request, order_id):
        auth = request.headers.get('Authorization', '')
        valid, _manager = verify_manager_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        new_status = request.data.get('status')
        if new_status not in self.ALLOWED_STATUS:
            return Response({
                'error': 'Trạng thái không hợp lệ',
                'allowed_status': sorted(self.ALLOWED_STATUS)
            }, status=400)

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)


class AdminOrderSummaryView(APIView):
    """Thống kê đơn hàng/doanh thu cho manager dashboard."""

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, manager = verify_manager_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        orders = Order.objects.all()
        total_orders = orders.count()
        delivered_orders = orders.filter(status='delivered').count()
        cancelled_orders = orders.filter(status='cancelled').count()
        pending_orders = orders.filter(status='pending').count()

        gross_revenue = orders.exclude(status='cancelled').aggregate(total=Sum('total_amount')).get('total') or 0
        delivered_revenue = orders.filter(status='delivered').aggregate(total=Sum('total_amount')).get('total') or 0

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_30_days = now - timedelta(days=30)

        month_orders = orders.filter(created_at__gte=month_start).count()
        month_revenue = orders.filter(created_at__gte=month_start).exclude(status='cancelled').aggregate(total=Sum('total_amount')).get('total') or 0

        recent_orders_qs = orders.filter(created_at__gte=last_30_days).exclude(status='cancelled')
        recent_orders_count = recent_orders_qs.count()
        recent_orders_revenue = recent_orders_qs.aggregate(total=Sum('total_amount')).get('total') or 0

        return Response({
            'actor': {'id': manager.get('id'), 'role': 'manager'},
            'summary': {
                'total_orders': total_orders,
                'delivered_orders': delivered_orders,
                'pending_orders': pending_orders,
                'cancelled_orders': cancelled_orders,
                'gross_revenue': float(gross_revenue),
                'delivered_revenue': float(delivered_revenue),
                'month_orders': month_orders,
                'month_revenue': float(month_revenue),
                'last_30_days_orders': recent_orders_count,
                'last_30_days_revenue': float(recent_orders_revenue),
            }
        })
