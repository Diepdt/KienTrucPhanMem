from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Laptop
from .serializers import LaptopSerializer, LaptopCreateSerializer

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
        catalog_url = django_settings.PRODUCT_SERVICE_URL
        resp = http_requests.get(f"{catalog_url}/api/categories/{category_id}/", timeout=5)
        if resp.status_code == 200:
            return resp.json().get('name', '')
    except Exception:
        pass
    return ''


class LaptopViewSet(viewsets.ViewSet):
    """Quản lý laptop - Staff có quyền CRUD, khách hàng chỉ được đọc."""

    def list(self, request):
        """Danh sách laptop - ai cũng xem được."""
        laptops = Laptop.objects.filter(is_active=True)
        # Lọc theo category nếu có
        category_id = request.query_params.get('category_id')
        if category_id:
            laptops = laptops.filter(category_id=category_id)
        
        # Tìm kiếm chung hoặc tách riêng
        search = request.query_params.get('search')
        if search:
            # Tìm cả name và brand
            from django.db.models import Q
            laptops = laptops.filter(Q(name__icontains=search) | Q(brand__icontains=search))
        else:
            # Tìm riêng từng field
            brand = request.query_params.get('brand')
            if brand:
                laptops = laptops.filter(brand__icontains=brand)
            name = request.query_params.get('name')
            if name:
                laptops = laptops.filter(name__icontains=name)
        
        return Response(LaptopSerializer(laptops, many=True).data)

    def retrieve(self, request, pk=None):
        """Chi tiết laptop."""
        try:
            laptop = Laptop.objects.get(id=pk, is_active=True)
            return Response(LaptopSerializer(laptop).data)
        except Laptop.DoesNotExist:
            return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Tạo laptop mới - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = LaptopCreateSerializer(data=request.data)
        if serializer.is_valid():
            laptop = serializer.save(created_by_staff_id=admin.get('id'))
            
            # Lấy tên category từ catalog-service
            if laptop.category_id:
                laptop.category_name = get_category_name(laptop.category_id)
                laptop.save()
            
            return Response(LaptopSerializer(laptop).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Cập nhật laptop - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            laptop = Laptop.objects.get(id=pk)
        except Laptop.DoesNotExist:
            return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LaptopCreateSerializer(laptop, data=request.data, partial=True)
        if serializer.is_valid():
            laptop = serializer.save()
            
            # Refresh category name
            if 'category_id' in request.data:
                laptop.category_name = get_category_name(request.data.get('category_id'))
                laptop.save()
            
            return Response(LaptopSerializer(laptop).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Xóa laptop (soft delete) - chỉ staff/manager."""
        auth_header = request.headers.get('Authorization', '')
        valid, admin = verify_admin_token(auth_header)
        
        if not valid:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            laptop = Laptop.objects.get(id=pk)
            laptop.is_active = False
            laptop.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Laptop.DoesNotExist:
            return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)


class LaptopDetailPublicView(APIView):
    """Chi tiết laptop cho public (dùng cho trang chi tiết)."""
    
    def get(self, request, pk):
        try:
            laptop = Laptop.objects.get(id=pk, is_active=True)
            return Response(LaptopSerializer(laptop).data)
        except Laptop.DoesNotExist:
            return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateStockView(APIView):
    """Cập nhật stock laptop (từ order-service sau khi đặt hàng)."""
    
    def patch(self, request):
        """
        Body: {"laptop_id": 1, "quantity": 2}
        Giảm stock khi khách đặt hàng
        """
        laptop_id = request.data.get('laptop_id')
        quantity = request.data.get('quantity', 0)
        
        try:
            laptop = Laptop.objects.get(id=laptop_id)
            if laptop.stock >= quantity:
                laptop.stock -= quantity
                laptop.save()
                return Response({
                    'id': laptop.id,
                    'stock': laptop.stock,
                    'message': 'Stock updated'
                })
            else:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Laptop.DoesNotExist:
            return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)
