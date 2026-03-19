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


class ClothViewSet(viewsets.ViewSet):
    def list(self, request):
        clothes = Cloth.objects.filter(is_active=True)

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
        valid, staff = verify_staff_token(auth)
        if not valid:
            return Response({'error': 'Chỉ nhân viên mới được thêm sản phẩm'}, status=403)

        serializer = ClothCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        cloth = serializer.save(created_by_staff_id=staff['id'])
        return Response(ClothSerializer(cloth).data, status=201)

    def update(self, request, pk=None):
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_staff_token(auth)
        if not valid:
            return Response({'error': 'Chỉ nhân viên mới được sửa sản phẩm'}, status=403)

        try:
            cloth = Cloth.objects.get(pk=pk)
        except Cloth.DoesNotExist:
            return Response({'error': 'Sản phẩm quần áo không tồn tại'}, status=404)

        serializer = ClothSerializer(cloth, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_staff_token(auth)
        if not valid:
            return Response({'error': 'Chỉ nhân viên mới được xóa sản phẩm'}, status=403)

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
