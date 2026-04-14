from rest_framework import serializers

from catalog.models import Category, Product


class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'product_type']


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        allow_null=True,
        required=False,
    )
    category = CategoryMiniSerializer(read_only=True)
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'product_type',
            'category',
            'category_id',
            'category_name',
            'price',
            'stock',
            'attributes',
            'description',
            'image_url',
            'is_active',
            'created_by_staff_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category', 'category_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category_id'] = instance.category_id
        return data

    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''

    def validate_product_type(self, value):
        normalized = str(value).strip().lower().replace(' ', '_')
        if not normalized:
            raise serializers.ValidationError('product_type is required')
        for char in normalized:
            if not (char.isalnum() or char in {'_', '-'}):
                raise serializers.ValidationError(
                    'product_type can only contain letters, numbers, underscore, and dash'
                )
        return normalized

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('stock cannot be negative')
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('price must be greater than 0')
        return value

    def validate_attributes(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError('attributes must be a JSON object')
        return value
