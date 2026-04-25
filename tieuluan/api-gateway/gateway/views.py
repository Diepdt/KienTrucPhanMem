from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings as django_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests as http_requests
import logging
import json

logger = logging.getLogger(__name__)

# Bảng định tuyến: prefix → URL service backend
ROUTE_TABLE = [
    ('staffs/', django_settings.STAFF_SERVICE_URL),
    ('staff/', django_settings.STAFF_SERVICE_URL),
    ('managers/', django_settings.MANAGER_SERVICE_URL),
    ('manager/', django_settings.MANAGER_SERVICE_URL),
    ('customers/', django_settings.CUSTOMER_SERVICE_URL),
    ('categories/', django_settings.PRODUCT_SERVICE_URL),
    ('products/', django_settings.PRODUCT_SERVICE_URL),
    ('carts/', django_settings.CART_SERVICE_URL),
    ('orders/', django_settings.ORDER_SERVICE_URL),
    ('shipping/', django_settings.SHIP_SERVICE_URL),
    ('payment/', django_settings.PAY_SERVICE_URL),
    ('reviews/', django_settings.COMMENT_SERVICE_URL),
    ('recommendations/', django_settings.RECOMMENDER_SERVICE_URL),
    ('chat/', django_settings.RECOMMENDER_SERVICE_URL),
    ('events/', django_settings.RECOMMENDER_SERVICE_URL),
]


def resolve_service(path):
    """Tìm service backend phù hợp dựa trên path prefix."""
    for prefix, service_url in ROUTE_TABLE:
        if path.startswith(prefix):
            return service_url
    return None


def standard_response(success, data=None, message='', code=200):
    return Response({
        'success': bool(success),
        'data': data,
        'message': message,
    }, status=code)


def is_blocked_path(path):
    normalized = '/' + str(path or '').strip('/') + '/'
    if '/internal/' in normalized:
        return True
    if normalized.startswith('/admin/'):
        return True
    return False


def build_upstream_response(resp):
    """Return upstream response as-is to preserve backward compatibility."""
    content_type = resp.headers.get('Content-Type', 'application/octet-stream')
    django_response = HttpResponse(
        content=resp.content,
        status=resp.status_code,
        content_type=content_type,
    )

    # Forward most upstream headers except hop-by-hop ones.
    skip_headers = {
        'connection',
        'keep-alive',
        'proxy-authenticate',
        'proxy-authorization',
        'te',
        'trailers',
        'transfer-encoding',
        'upgrade',
        'content-length',
    }
    for header, value in resp.headers.items():
        if header.lower() in skip_headers:
            continue
        django_response[header] = value

    return django_response


class ProxyView(APIView):
    """
    API Gateway - Proxy tất cả request đến các microservice phù hợp.
    
    Bảng định tuyến:
    - /api/staffs/*         → staff-service:8001
    - /api/staff/*          → staff-service:8001
    - /api/managers/*       → manager-service:8002
    - /api/manager/*        → manager-service:8002
    - /api/customers/*      → customer-service:8003
    - /api/categories/*     → product-service:8004
    - /api/products/*       → product-service:8004
    - /api/carts/*          → cart-service:8006
    - /api/orders/*         → order-service:8007
    - /api/shipping/*       → ship-service:8008
    - /api/payment/*        → pay-service:8009
    - /api/reviews/*        → comment-rate-service:8010
    - /api/recommendations/* → recommender-ai-service:8011
    - /api/chat/*           → recommender-ai-service:8011
    - /api/events/*         → recommender-ai-service:8011
    """

    def _proxy(self, request, path):
        raw_query = request.META.get('QUERY_STRING', '')

        if is_blocked_path(path):
            return standard_response(False, None, 'Forbidden endpoint', 403)

        service_url = resolve_service(path)
        if not service_url:
            return standard_response(
                False,
                {
                    'available_routes': [p for p, _ in ROUTE_TABLE],
                    'path': path,
                },
                'Route không tồn tại',
                404,
            )

        target_url = f"{service_url}/api/{path}"
        if raw_query:
            target_url += f"?{raw_query}"

        # Chuyển tiếp tất cả headers gốc (trừ host)
        headers = {
            key.replace('HTTP_', '').replace('_', '-').title(): value
            for key, value in request.META.items()
            if key.startswith('HTTP_') and key != 'HTTP_HOST'
        }
        headers['Content-Type'] = request.content_type or 'application/json'

        method = request.method.lower()
        try:
            # When client sent JSON, forward as JSON to preserve content-type and encoding
            send_kwargs = dict(headers=headers, timeout=30, allow_redirects=False)
            content_type = headers.get('Content-Type', '')
            if content_type and content_type.split(';')[0].strip().lower() == 'application/json':
                try:
                    body_json = json.loads(request.body.decode('utf-8') or '{}')
                    resp = getattr(http_requests, method)(target_url, json=body_json, **send_kwargs)
                except Exception:
                    # fallback to raw body if parsing fails
                    resp = getattr(http_requests, method)(target_url, data=request.body, **send_kwargs)
            else:
                resp = getattr(http_requests, method)(target_url, data=request.body, **send_kwargs)
            return build_upstream_response(resp)

        except http_requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to service at {service_url}")
            return standard_response(False, None, f'Service không khả dụng: {service_url}', 503)
        except http_requests.exceptions.Timeout:
            return standard_response(False, None, 'Service timeout', 504)
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            return standard_response(False, None, 'Lỗi gateway nội bộ', 502)

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


def serve_customer_profile(request):
    return render(request, 'client/profile.html')


def serve_customer_agent(request):
    return render(request, 'client/agent-chat.html')


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


def serve_admin_categories(request):
    return render(request, 'admin/category-list.html')


def serve_admin_reviews(request):
    return render(request, 'admin/review-list.html')


def serve_admin_profile(request):
    return render(request, 'admin/profile.html')


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
            'product-service': django_settings.PRODUCT_SERVICE_URL,
            'cart-service': django_settings.CART_SERVICE_URL,
            'order-service': django_settings.ORDER_SERVICE_URL,
            'ship-service': django_settings.SHIP_SERVICE_URL,
            'pay-service': django_settings.PAY_SERVICE_URL,
            'comment-rate-service': django_settings.COMMENT_SERVICE_URL,
            'recommender-ai-service': django_settings.RECOMMENDER_SERVICE_URL,
        }
        status_info = {}
        for name, url in SERVICES.items():
            try:
                resp = http_requests.get(f"{url}/api/", timeout=3)
                status_info[name] = {
                    'status': 'up' if resp.status_code < 500 else 'down',
                    'url': url,
                    'status_code': resp.status_code,
                }
            except Exception:
                status_info[name] = {'status': 'down', 'url': url}

        all_up = all(v['status'] == 'up' for v in status_info.values())
        return standard_response(
            True,
            {
                'gateway': 'up',
                'services': status_info,
                'overall': 'healthy' if all_up else 'degraded',
            },
            'Gateway health summary',
            200,
        )
