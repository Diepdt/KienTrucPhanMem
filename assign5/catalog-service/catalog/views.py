from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD danh mục sách."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        # Chỉ trả về danh mục gốc (không có parent), kèm sub-categories
        top_level = Category.objects.filter(parent=None)
        return Response(CategorySerializer(top_level, many=True).data)

    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
