from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PaymentMethod, Payment
from .serializers import PaymentMethodSerializer, PaymentSerializer


class PaymentMethodListView(APIView):
    """Danh sách phương thức thanh toán."""
    def get(self, request):
        methods = PaymentMethod.objects.filter(is_active=True)
        return Response(PaymentMethodSerializer(methods, many=True).data)

    def post(self, request):
        serializer = PaymentMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PaymentMethodDetailView(APIView):
    """Chi tiết một phương thức thanh toán - gọi từ order-service."""
    def get(self, request, pk):
        try:
            method = PaymentMethod.objects.get(pk=pk, is_active=True)
            return Response(PaymentMethodSerializer(method).data)
        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=404)


class CreatePaymentView(APIView):
    """Tạo giao dịch thanh toán - gọi từ order-service."""
    def post(self, request):
        order_id = request.data.get('order_id')
        method_id = request.data.get('payment_method_id')
        amount = request.data.get('amount')
        if not all([order_id, method_id, amount]):
            return Response({'error': 'order_id, payment_method_id, amount bắt buộc'}, status=400)
        try:
            method = PaymentMethod.objects.get(pk=method_id)
        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Phương thức thanh toán không tồn tại'}, status=404)
        payment = Payment.objects.create(
            order_id=order_id, method=method,
            method_name=method.name, amount=amount
        )
        return Response(PaymentSerializer(payment).data, status=201)


class PaymentByOrderView(APIView):
    """Lấy thông tin thanh toán theo order_id."""
    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=404)

    def patch(self, request, order_id):
        """Cập nhật trạng thái thanh toán (sau khi khách hàng hoàn tất)."""
        try:
            payment = Payment.objects.get(order_id=order_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=404)
        new_status = request.data.get('status')
        if new_status:
            payment.status = new_status
            payment.save()
        return Response(PaymentSerializer(payment).data)
