import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(lookup_expr='icontains')
    product_name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = ['category', 'product_name', 'min_price', 'max_price'] 