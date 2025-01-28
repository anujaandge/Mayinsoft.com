from .models import Product

def categories_processor(request):
    """
    Add categories to all templates.
    """
    categories = Product.objects.values_list('category', flat=True).distinct()
    return {'categories': categories}
