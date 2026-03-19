from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings as django_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests as http_requests
import logging

logger = logging.getLogger(__name__)

# Bảng định tuyến: prefix → URL service backend
ROUTE_TABLE = [
    ('staffs/', django_settings.STAFF_SERVICE_URL),
    ('staff/', django_settings.STAFF_SERVICE_URL),
    ('managers/', django_settings.MANAGER_SERVICE_URL),
    ('manager/', django_settings.MANAGER_SERVICE_URL),
    ('customers/', django_settings.CUSTOMER_SERVICE_URL),
    ('categories/', django_settings.CATALOG_SERVICE_URL),
    ('books/', django_settings.BOOK_SERVICE_URL),
    ('carts/', django_settings.CART_SERVICE_URL),
    ('orders/', django_settings.ORDER_SERVICE_URL),
    ('shipping/', django_settings.SHIP_SERVICE_URL),
    ('payment/', django_settings.PAY_SERVICE_URL),
    ('reviews/', django_settings.COMMENT_SERVICE_URL),
    ('recommendations/', django_settings.RECOMMENDER_SERVICE_URL),
    ('clothes/', django_settings.CLOTH_SERVICE_URL),
    ('agent/',            django_settings.AGENT_SERVICE_URL),
]


def resolve_service(path):
    """Tìm service backend phù hợp dựa trên path prefix."""
    for prefix, service_url in ROUTE_TABLE:
        if path.startswith(prefix):
            return service_url
    return None


class ProxyView(APIView):
    """
    API Gateway - Proxy tất cả request đến các microservice phù hợp.
    
    Bảng định tuyến:
    - /api/staffs/*         → staff-service:8001
    - /api/staff/*          → staff-service:8001
    - /api/managers/*       → manager-service:8002
    - /api/manager/*        → manager-service:8002
    - /api/customers/*      → customer-service:8003
    - /api/categories/*     → catalog-service:8004
    - /api/books/*          → book-service:8005
    - /api/carts/*          → cart-service:8006
    - /api/orders/*         → order-service:8007
    - /api/shipping/*       → ship-service:8008
    - /api/payment/*        → pay-service:8009
    - /api/reviews/*        → comment-rate-service:8010
    - /api/recommendations/* → recommender-ai-service:8011
    - /api/clothes/*        → cloth-service:8013
    """

    def _proxy(self, request, path):
        service_url = resolve_service(path)
        if not service_url:
            return Response({
                'error': 'Route không tồn tại',
                'available_routes': [p for p, _ in ROUTE_TABLE],
                'path': path
            }, status=404)

        target_url = f"{service_url}/api/{path}"
        if request.META.get('QUERY_STRING'):
            target_url += f"?{request.META['QUERY_STRING']}"

        # Chuyển tiếp tất cả headers gốc (trừ host)
        headers = {
            key.replace('HTTP_', '').replace('_', '-').title(): value
            for key, value in request.META.items()
            if key.startswith('HTTP_') and key != 'HTTP_HOST'
        }
        headers['Content-Type'] = request.content_type or 'application/json'

        method = request.method.lower()
        try:
            resp = getattr(http_requests, method)(
                target_url,
                headers=headers,
                data=request.body,
                timeout=30,
                allow_redirects=False
            )
            content_type = resp.headers.get('Content-Type', 'application/json')
            django_response = HttpResponse(
                content=resp.content,
                status=resp.status_code,
                content_type=content_type
            )
            # Chuyển tiếp một số headers quan trọng
            for header in ('X-Total-Count', 'X-Page', 'Location'):
                if header in resp.headers:
                    django_response[header] = resp.headers[header]
            return django_response

        except http_requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to service at {service_url}")
            return Response({'error': f'Service không khả dụng: {service_url}'}, status=503)
        except http_requests.exceptions.Timeout:
            return Response({'error': 'Service timeout'}, status=504)
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            return Response({'error': 'Lỗi gateway nội bộ'}, status=502)

    def get(self, request, path=''):
        return self._proxy(request, path)

    def post(self, request, path=''):
        return self._proxy(request, path)

    def put(self, request, path=''):
        return self._proxy(request, path)

    def patch(self, request, path=''):
        return self._proxy(request, path)

    def delete(self, request, path=''):
        return self._proxy(request, path)


def serve_portal(request):
    return redirect('user-login-page')


def serve_user_login(request):
    return render(request, 'user/login.html')


def serve_user_register(request):
    return render(request, 'user/register.html')


def serve_customer_frontend(request):
    return render(request, 'client/home.html')


def serve_customer_product(request):
    return render(request, 'client/product.html')


def serve_customer_product_detail(request):
    return render(request, 'client/product-detail.html')


def serve_customer_cart(request):
    return render(request, 'client/cart.html')


def serve_customer_checkout(request):
    return render(request, 'client/checkout.html')


def serve_customer_order_history(request):
    return render(request, 'client/order-history.html')


def serve_customer_order_detail(request, order_id):
    return render(request, 'client/order-detail.html')


def serve_admin_frontend(request):
    return render(request, 'admin/dashboard.html')


def serve_admin_users(request):
    return render(request, 'admin/user-list.html')


def serve_admin_users_create(request):
    return render(request, 'admin/user-create.html')


def serve_admin_users_detail(request):
    return render(request, 'admin/user-detail.html')


def serve_admin_products(request):
    return render(request, 'admin/product-list.html')


def serve_admin_products_create(request):
    return render(request, 'admin/product-create.html')


def serve_admin_products_detail(request):
    return render(request, 'admin/product-detail.html')


def serve_admin_orders(request):
    return render(request, 'admin/order-list.html')


def serve_status_403(request):
    return render(request, 'status/403.html', status=403)


def serve_status_404(request):
    return render(request, 'status/404.html', status=404)


def serve_status_500(request):
    return render(request, 'status/500.html', status=500)


class HealthCheckView(APIView):
    """Kiểm tra trạng thái tất cả services."""

    def get(self, request):
        SERVICES = {
            'staff-service': django_settings.STAFF_SERVICE_URL,
            'manager-service': django_settings.MANAGER_SERVICE_URL,
            'customer-service': django_settings.CUSTOMER_SERVICE_URL,
            'catalog-service': django_settings.CATALOG_SERVICE_URL,
            'book-service': django_settings.BOOK_SERVICE_URL,
            'cart-service': django_settings.CART_SERVICE_URL,
            'order-service': django_settings.ORDER_SERVICE_URL,
            'ship-service': django_settings.SHIP_SERVICE_URL,
            'pay-service': django_settings.PAY_SERVICE_URL,
            'comment-rate-service': django_settings.COMMENT_SERVICE_URL,
            'recommender-ai-service': django_settings.RECOMMENDER_SERVICE_URL,
            'cloth-service': django_settings.CLOTH_SERVICE_URL,
        }
        status_info = {}
        for name, url in SERVICES.items():
            try:
                resp = http_requests.get(f"{url}/api/", timeout=3)
                status_info[name] = {'status': 'up', 'url': url}
            except Exception:
                status_info[name] = {'status': 'down', 'url': url}

        all_up = all(v['status'] == 'up' for v in status_info.values())
        return Response({
            'gateway': 'up',
            'services': status_info,
            'overall': 'healthy' if all_up else 'degraded'
        }, status=200)
