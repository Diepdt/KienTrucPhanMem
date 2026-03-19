from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.conf import settings as django_settings
import requests as http_requests
import logging

from .models import Book
from .serializers import BookSerializer, BookCreateSerializer

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


class BookViewSet(viewsets.ViewSet):
    """Quản lý sách - Staff có quyền CRUD, khách hàng chỉ được đọc."""

    def list(self, request):
        """Danh sách sách - ai cũng xem được."""
        books = Book.objects.filter(is_active=True)
        # Lọc theo category nếu có
        category_id = request.query_params.get('category_id')
        if category_id:
            books = books.filter(category_id=category_id)
        
        # Tìm kiếm chung hoặc tách riêng
        search = request.query_params.get('search')
        if search:
            # Tìm cả title và author
            from django.db.models import Q
            books = books.filter(Q(title__icontains=search) | Q(author__icontains=search))
        else:
            # Tìm riêng từng field (backward compatible)
            author = request.query_params.get('author')
            if author:
                books = books.filter(author__icontains=author)
            title = request.query_params.get('title')
            if title:
                books = books.filter(title__icontains=title)
        return Response(BookSerializer(books, many=True).data)

    def retrieve(self, request, pk=None):
        """Chi tiết một cuốn sách."""
        try:
            book = Book.objects.get(pk=pk, is_active=True)
            return Response(BookSerializer(book).data)
        except Book.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)

    def create(self, request):
        """Tạo sách mới - staff/manager."""
        auth = request.headers.get('Authorization', '')
        valid, actor = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ admin/staff mới được thêm sách'}, status=403)

        serializer = BookCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Lấy tên danh mục
        category_id = request.data.get('category_id')
        category_name = get_category_name(category_id) if category_id else ''

        book = serializer.save(
            created_by_staff_id=actor['id'],
            category_name=category_name
        )
        return Response(BookSerializer(book).data, status=201)

    def update(self, request, pk=None):
        """Cập nhật sách - staff/manager."""
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ admin/staff mới được sửa sách'}, status=403)
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)

        payload = request.data.copy()
        if 'category_id' in payload:
            category_id = payload.get('category_id')
            payload['category_name'] = get_category_name(category_id) if category_id else ''

        serializer = BookCreateSerializer(book, data=payload, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(BookSerializer(book).data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        """Xóa sách (soft delete) - staff/manager."""
        auth = request.headers.get('Authorization', '')
        valid, _ = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Chỉ admin/staff mới được xóa sách'}, status=403)
        try:
            book = Book.objects.get(pk=pk)
            book.is_active = False
            book.save()
            return Response({'message': 'Sách đã được xóa'})
        except Book.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)


class BookDetailPublicView(APIView):
    """API public lấy thông tin sách (dành cho cart-service, order-service gọi)."""

    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk, is_active=True)
            return Response(BookSerializer(book).data)
        except Book.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)


class UpdateStockView(APIView):
    """Cập nhật tồn kho - gọi từ order-service."""

    def post(self, request):
        items = request.data.get('items', [])
        errors = []
        for item in items:
            book_id = item.get('book_id')
            quantity = item.get('quantity', 0)
            try:
                book = Book.objects.get(pk=book_id)
                if book.stock < quantity:
                    errors.append({'book_id': book_id, 'error': 'Không đủ hàng'})
                else:
                    book.stock -= quantity
                    book.save()
            except Book.DoesNotExist:
                errors.append({'book_id': book_id, 'error': 'Sách không tồn tại'})
        if errors:
            return Response({'errors': errors}, status=400)
        return Response({'message': 'Tồn kho đã được cập nhật'})
