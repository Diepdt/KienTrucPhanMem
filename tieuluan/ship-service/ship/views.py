from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta
from .models import ShippingMethod, Shipment
from .serializers import ShippingMethodSerializer, ShipmentSerializer


class ShippingMethodListView(APIView):
    """Danh sách phương thức vận chuyển."""
    def get(self, request):
        methods = ShippingMethod.objects.filter(is_active=True)
        return Response(ShippingMethodSerializer(methods, many=True).data)

    def post(self, request):
        serializer = ShippingMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShippingMethodDetailView(APIView):
    """Chi tiết một phương thức vận chuyển - gọi từ order-service."""
    def get(self, request, pk):
        try:
            method = ShippingMethod.objects.get(pk=pk, is_active=True)
            return Response(ShippingMethodSerializer(method).data)
        except ShippingMethod.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=404)


class CreateShipmentView(APIView):
    """Tạo lô vận chuyển - gọi từ order-service."""
    def post(self, request):
        order_id = request.data.get('order_id')
        method_id = request.data.get('shipping_method_id')
        address = request.data.get('shipping_address', '')
        if not all([order_id, method_id, address]):
            return Response({'error': 'order_id, shipping_method_id, shipping_address bắt buộc'}, status=400)
        try:
            method = ShippingMethod.objects.get(pk=method_id)
        except ShippingMethod.DoesNotExist:
            return Response({'error': 'Phương thức vận chuyển không tồn tại'}, status=404)
        estimated = date.today() + timedelta(days=method.delivery_days)
        shipment = Shipment.objects.create(
            order_id=order_id, method=method,
            method_name=method.name, shipping_address=address,
            estimated_delivery=estimated
        )
        return Response(ShipmentSerializer(shipment).data, status=201)


class ShipmentByOrderView(APIView):
    """Lấy thông tin vận chuyển theo order_id."""
    def get(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            return Response(ShipmentSerializer(shipment).data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy vận chuyển'}, status=404)

    def patch(self, request, order_id):
        """Cập nhật trạng thái vận chuyển."""
        try:
            shipment = Shipment.objects.get(order_id=order_id)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy vận chuyển'}, status=404)
        new_status = request.data.get('status')
        if new_status:
            shipment.status = new_status
            shipment.save()
        return Response(ShipmentSerializer(shipment).data)
