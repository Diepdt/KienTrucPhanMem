from rest_framework import status, viewsets
from rest_framework.response import Response

from catalog.application.services import CategoryApplicationService
from catalog.infrastructure.repositories import DjangoCategoryRepository
from catalog.presentation.api.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = CategoryApplicationService(DjangoCategoryRepository())

    def get_queryset(self):
        return self.service.list_categories(self.request.query_params)

    def list(self, request):
        categories = self.service.list_categories(request.query_params)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        category = self.service.get_category(kwargs.get('pk'))
        if not category:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(category).data)

    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            category = self.service.create_category(serializer.validated_data)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(category).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.service.get_category(kwargs.get('pk'))
        if not instance:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            category = self.service.update_category(kwargs.get('pk'), serializer.validated_data)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(category).data)

    def destroy(self, request, *args, **kwargs):
        deleted = self.service.delete_category(kwargs.get('pk'))
        if not deleted:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
