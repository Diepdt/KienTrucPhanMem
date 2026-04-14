from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Cloth
from .serializers import ClothSerializer, ClothCreateSerializer

logger = logging.getLogger(__name__)


def verify_staff_token(auth_header):
    try:
        staff_url = django_settings.STAFF_SERVICE_URL
        resp = http_requests.get(
            f"{staff_url}/api/staff/verify-token/",
            headers={'Authorization': auth_header},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('valid', False), data.get('staff')
    except Exception as e:
        logger.error(f"Error verifying staff token: {e}")
    return False, None


def verify_manager_token(auth_header):
    try:
        manager_url = django_settings.MANAGER_SERVICE_URL
        resp = http_requests.get(
            f"{manager_url}/api/manager/verify-token/",
            headers={'Authorization': auth_header},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('valid', False), data.get('manager')
    except Exception as e:
        logger.error(f"Error verifying manager token: {e}")
    return False, None


def verify_admin_token(auth_header):
    staff_valid, staff = verify_staff_token(auth_header)
    if staff_valid:
        return True, {'id': staff.get('id'), 'type': 'staff'}

    manager_valid, manager = verify_manager_token(auth_header)
    if manager_valid:
        return True, {'id': manager.get('id'), 'type': 'manager'}

    return False, None


def get_category_name(category_id):
    try:
        catalog_url = django_settings.PRODUCT_SERVICE_URL
        resp = http_requests.get(f"{catalog_url}/api/categories/{category_id}/", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('name', '')
    except Exception as e:
        logger.error(f"Error getting category name: {e}")
    return ''


class ClothViewSet(viewsets.ViewSet):
    def list(self, request):
        clothes = Cloth.objects.filter(is_active=True)

        category_id = request.query_params.get('category_id')
        if category_id:
            clothes = clothes.filter(category_id=category_id)

        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            clothes = clothes.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(color__icontains=search) |
                Q(material__icontains=search)
            )

        name = request.query_params.get('name')
        if name:
            clothes = clothes.filter(name__icontains=name)

        brand = request.query_params.get('brand')
        if brand:
            clothes = clothes.filter(brand__icontains=brand)

        size = request.query_params.get('size')
        if size:
            clothes = clothes.filter(size__iexact=size)

        color = request.query_params.get('color')
        if color:
            clothes = clothes.filter(color__icontains=color)

        return Response(ClothSerializer(clothes, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            cloth = Cloth.objects.get(pk=pk, is_active=True)
            return Response(ClothSerializer(cloth).data)
        except Cloth.DoesNotExist:
            return Response({'error': 'Sản phẩm quần áo không tồn tại'}, status=404)

    def create(self, request):
        auth = request.headers.get('Authorization', '')
        valid, actor = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ manager/staff mới được thêm sản phẩm'}, status=403)

        serializer = ClothCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        category_id = request.data.get('category_id')
        category_name = get_category_name(category_id) if category_id else ''
        cloth = serializer.save(
            created_by_staff_id=actor['id'],
            category_name=category_name
        )
        return Response(ClothSerializer(cloth).data, status=201)

    def update(self, request, pk=None):
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ manager/staff mới được sửa sản phẩm'}, status=403)

        try:
            cloth = Cloth.objects.get(pk=pk)
        except Cloth.DoesNotExist:
            return Response({'error': 'Sản phẩm quần áo không tồn tại'}, status=404)

        payload = request.data.copy()
        if 'category_id' in payload:
            category_id = payload.get('category_id')
            payload['category_name'] = get_category_name(category_id) if category_id else ''

        serializer = ClothSerializer(cloth, data=payload, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ manager/staff mới được xóa sản phẩm'}, status=403)

        try:
            cloth = Cloth.objects.get(pk=pk)
            cloth.is_active = False
            cloth.save()
            return Response({'message': 'Sản phẩm đã được xóa'})
        except Cloth.DoesNotExist:
            return Response({'error': 'Sản phẩm quần áo không tồn tại'}, status=404)


class ClothDetailPublicView(APIView):
    def get(self, request, pk):
        try:
            cloth = Cloth.objects.get(pk=pk, is_active=True)
            return Response(ClothSerializer(cloth).data)
        except Cloth.DoesNotExist:
            return Response({'error': 'Sản phẩm quần áo không tồn tại'}, status=404)


class UpdateStockView(APIView):
    def post(self, request):
        items = request.data.get('items', [])
        errors = []

        for item in items:
            cloth_id = item.get('cloth_id')
            quantity = item.get('quantity', 0)
            try:
                cloth = Cloth.objects.get(pk=cloth_id)
                if cloth.stock < quantity:
                    errors.append({'cloth_id': cloth_id, 'error': 'Không đủ hàng'})
                else:
                    cloth.stock -= quantity
                    cloth.save()
            except Cloth.DoesNotExist:
                errors.append({'cloth_id': cloth_id, 'error': 'Sản phẩm không tồn tại'})

        if errors:
            return Response({'errors': errors}, status=400)
        return Response({'message': 'Tồn kho quần áo đã được cập nhật'})
