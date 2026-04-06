from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD danh mục sách - hỗ trợ lọc theo product_type."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        """
        Lấy danh mục gốc (parent=None) kèm subcategories.
        Hỗ trợ filter theo product_type: ?product_type=book
        """
        product_type = request.query_params.get('product_type', '').strip()
        
        # Danh mục gốc
        top_level = Category.objects.filter(parent=None)
        
        # Lọc theo product_type nếu có
        if product_type:
            top_level = top_level.filter(product_type=product_type)
        
        serializer = CategorySerializer(top_level, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Tạo danh mục mới. Yêu cầu product_type.
        """
        # Validate product_type
        product_type = request.data.get('product_type', '').strip()
        if not product_type:
            return Response(
                {'error': 'product_type field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate name
        name = request.data.get('name', '').strip()
        if not name:
            return Response(
                {'error': 'name field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Cập nhật danh mục. Hỗ trợ cập nhật product_type.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CategorySerializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
