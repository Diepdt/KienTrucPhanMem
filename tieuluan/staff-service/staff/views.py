from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Staff, StaffToken
from .serializers import StaffSerializer, StaffCreateSerializer, LoginSerializer


def get_staff_from_token(request):
    """Helper: xác thực staff từ Authorization header."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    key = auth.split(' ', 1)[1]
    try:
        token = StaffToken.objects.get(key=key)
        return token.staff if token.staff.is_active else None
    except StaffToken.DoesNotExist:
        return None


class StaffViewSet(viewsets.ModelViewSet):
    """CRUD nhân viên - chỉ manager mới có quyền (kiểm tra token header)."""
    queryset = Staff.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return StaffCreateSerializer
        return StaffSerializer

    def list(self, request):
        staffs = Staff.objects.all()
        return Response(StaffSerializer(staffs, many=True).data)

    def create(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response(StaffSerializer(staff).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            staff = Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        try:
            staff = Staff.objects.get(pk=pk)
            staff.is_active = False
            staff.save()
            return Response({'message': 'Staff deactivated'})
        except Staff.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class StaffLoginView(APIView):
    """Đăng nhập nhân viên, trả về token."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)
        if not staff.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=401)
        if not staff.is_active:
            return Response({'error': 'Tài khoản hiện đang bị cấm'}, status=401)
        token, _ = StaffToken.objects.get_or_create(
            staff=staff,
            defaults={'key': StaffToken.generate_key()}
        )
        return Response({
            'token': token.key,
            'staff': StaffSerializer(staff).data
        })


class StaffLogoutView(APIView):
    """Đăng xuất, xóa token."""

    def post(self, request):
        staff = get_staff_from_token(request)
        if not staff:
            return Response({'error': 'Unauthorized'}, status=401)
        StaffToken.objects.filter(staff=staff).delete()
        return Response({'message': 'Logged out'})


class VerifyTokenView(APIView):
    """Xác thực token - được gọi bởi các service khác."""

    def get(self, request):
        staff = get_staff_from_token(request)
        if not staff:
            return Response({'valid': False, 'staff': None}, status=401)
        return Response({'valid': True, 'staff': StaffSerializer(staff).data})
