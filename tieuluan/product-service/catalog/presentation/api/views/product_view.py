from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.application.services import ProductApplicationService
from catalog.infrastructure.attributes_store import MongoProductAttributesStore
from catalog.infrastructure.repositories import DjangoProductRepository
from catalog.presentation.api.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProductApplicationService(DjangoProductRepository())
        self.attributes_store = MongoProductAttributesStore()

    def _inject_mongo_attributes(self, data):
        if isinstance(data, list):
            id_list = [item.get('id') for item in data if item.get('id') is not None]
            attributes_map = self.attributes_store.get_many(id_list)
            for item in data:
                product_id = item.get('id')
                if product_id in attributes_map:
                    item['attributes'] = attributes_map[product_id]
            return data

        if isinstance(data, dict):
            product_id = data.get('id')
            if product_id is not None:
                data['attributes'] = self.attributes_store.get(product_id, data.get('attributes'))
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            payload = self._inject_mongo_attributes(serializer.data)
            return self.get_paginated_response(payload)

        serializer = self.get_serializer(queryset, many=True)
        payload = self._inject_mongo_attributes(serializer.data)
        return Response(payload)

    def get_queryset(self):
        return self.service.list_products(self.request.query_params)

    def retrieve(self, request, *args, **kwargs):
        product = self.service.get_product(kwargs.get('pk'))
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        payload = self.get_serializer(product).data
        return Response(self._inject_mongo_attributes(payload))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.service.create_product(serializer.validated_data)

        # Persist flexible attributes to MongoDB while keeping relational data in MySQL.
        attributes = serializer.validated_data.get('attributes', {})
        self.attributes_store.upsert(product.id, attributes)

        payload = self.get_serializer(product).data
        return Response(self._inject_mongo_attributes(payload), status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        existing = self.service.get_product(kwargs.get('pk'))
        if not existing:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(existing, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = self.service.update_product(kwargs.get('pk'), serializer.validated_data)

        if 'attributes' in serializer.validated_data:
            merged_attributes = serializer.validated_data.get('attributes', {})
        else:
            merged_attributes = self.attributes_store.get(product.id, existing.attributes)
        self.attributes_store.upsert(product.id, merged_attributes)

        payload = self.get_serializer(product).data
        return Response(self._inject_mongo_attributes(payload))

    def destroy(self, request, *args, **kwargs):
        deleted = self.service.delete_product(kwargs.get('pk'))
        if not deleted:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        self.attributes_store.delete(kwargs.get('pk'))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductInventoryUpdateView(APIView):
    def post(self, request):
        items = request.data.get('items')
        if not isinstance(items, list) or not items:
            return Response({'error': 'items must be a non-empty list'}, status=400)

        service = ProductApplicationService(DjangoProductRepository())
        result = service.update_inventory(items)

        if not result['success']:
            return Response({'success': False, 'errors': result['errors']}, status=400)

        return Response({'success': True, 'updated': result['updated']}, status=200)
