from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.conf import settings as django_settings
import requests as http_requests
from .models import Manager, ManagerToken
from .serializers import ManagerSerializer, ManagerCreateSerializer, LoginSerializer


def get_manager_from_token(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    key = auth.split(' ', 1)[1]
    try:
        token = ManagerToken.objects.get(key=key)
        return token.manager if token.manager.is_active else None
    except ManagerToken.DoesNotExist:
        return None


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ManagerCreateSerializer
        return ManagerSerializer

    def list(self, request):
        managers = Manager.objects.filter(is_active=True)
        return Response(ManagerSerializer(managers, many=True).data)

    def create(self, request):
        serializer = ManagerCreateSerializer(data=request.data)
        if serializer.is_valid():
            mgr = serializer.save()
            return Response(ManagerSerializer(mgr).data, status=201)
        return Response(serializer.errors, status=400)


class ManagerLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            mgr = Manager.objects.get(email=email, is_active=True)
        except Manager.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=401)
        if not mgr.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=401)
        token, _ = ManagerToken.objects.get_or_create(
            manager=mgr, defaults={'key': ManagerToken.generate_key()})
        return Response({'token': token.key, 'manager': ManagerSerializer(mgr).data})


class VerifyTokenView(APIView):
    """Xác thực manager token - các service khác gọi."""
    def get(self, request):
        mgr = get_manager_from_token(request)
        if not mgr:
            return Response({'valid': False}, status=401)
        return Response({'valid': True, 'manager': ManagerSerializer(mgr).data})


class ManageStaffView(APIView):
    """Manager tạo/quản lý staff (gọi staff-service)."""

    def get(self, request):
        mgr = get_manager_from_token(request)
        if not mgr:
            return Response({'error': 'Unauthorized'}, status=401)
        staff_url = django_settings.STAFF_SERVICE_URL
        resp = http_requests.get(f"{staff_url}/api/staffs/",
                                 headers={'Authorization': request.headers.get('Authorization', '')})
        return Response(resp.json(), status=resp.status_code)

    def post(self, request):
        mgr = get_manager_from_token(request)
        if not mgr:
            return Response({'error': 'Unauthorized'}, status=401)
        staff_url = django_settings.STAFF_SERVICE_URL
        resp = http_requests.post(f"{staff_url}/api/staffs/", json=request.data)
        return Response(resp.json(), status=resp.status_code)
