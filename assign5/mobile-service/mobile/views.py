from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Mobile
from .serializers import MobileSerializer, MobileCreateSerializer

logger = logging.getLogger(__name__)

def verify_staff_token(auth_header):
    """Xác thực staff qua staff-service."""
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
    """Xác thực manager qua manager-service."""
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
    """Xác thực token của staff hoặc manager."""
    staff_valid, staff = verify_staff_token(auth_header)
    if staff_valid:
        return True, {'id': staff.get('id'), 'type': 'staff'}
    manager_valid, manager = verify_manager_token(auth_header)
    if manager_valid:
        return True, {'id': manager.get('id'), 'type': 'manager'}
    return False, None

def get_category_name(category_id):
    """Lấy tên danh mục từ catalog-service."""
    try:
        catalog_url = django_settings.CATALOG_SERVICE_URL
        resp = http_requests.get(f"{catalog_url}/api/categories/{category_id}/", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('name', '')
    except Exception:
        pass
    return ''

class MobileViewSet(viewsets.ViewSet):
    """Quản lý mobile - Staff có quyền CRUD, khách hàng chỉ được đọc."""

    def list(self, request):
        """Danh sách mobile - ai cũng xem được."""
        mobiles = Mobile.objects.filter(is_active=True)
        category_id = request.query_params.get('category_id')
        if category_id:
            mobiles = mobiles.filter(category_id=category_id)
        
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            mobiles = mobiles.filter(Q(name__icontains=search) | Q(brand__icontains=search))
        else:
            brand = request.query_params.get('brand')
            if brand:
                mobiles = mobiles.filter(brand__icontains=brand)
            name = request.query_params.get('name')
            if name:
                mobiles = mobiles.filter(name__icontains=name)
        
        return Response(MobileSerializer(mobiles, many=True).data)

    def retrieve(self, request, pk=None):
        """Chi tiết mobile."""
        try:
            mobile = Mobile.objects.get(id=pk, is_active=True)
            return Response(MobileSerializer(mobile).data)
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Tạo mobile mới - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = MobileCreateSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.save(created_by_staff_id=admin.get('id'))
            if mobile.category_id:
                mobile.category_name = get_category_name(mobile.category_id)
                mobile.save()
            return Response(MobileSerializer(mobile).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Cập nhật mobile - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            mobile = Mobile.objects.get(id=pk)
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MobileCreateSerializer(mobile, data=request.data, partial=True)
        if serializer.is_valid():
            mobile = serializer.save()
            if 'category_id' in request.data:
                mobile.category_name = get_category_name(request.data.get('category_id'))
                mobile.save()
            return Response(MobileSerializer(mobile).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Xóa mobile (soft delete) - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            mobile = Mobile.objects.get(id=pk)
            mobile.is_active = False
            mobile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)

class MobileDetailPublicView(APIView):
    """Chi tiết mobile cho public."""
    
    def get(self, request, pk):
        try:
            mobile = Mobile.objects.get(id=pk, is_active=True)
            return Response(MobileSerializer(mobile).data)
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateStockView(APIView):
    """Cập nhật stock mobile (từ order-service)."""
    
    def patch(self, request):
        """Body: {"mobile_id": 1, "quantity": 2}"""
        mobile_id = request.data.get('mobile_id')
        quantity = request.data.get('quantity', 0)
        
        try:
            mobile = Mobile.objects.get(id=mobile_id)
            if mobile.stock >= quantity:
                mobile.stock -= quantity
                mobile.save()
                return Response({
                    'id': mobile.id,
                    'stock': mobile.stock,
                    'message': 'Stock updated'
                })
            else:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Mobile.DoesNotExist:
            return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)
