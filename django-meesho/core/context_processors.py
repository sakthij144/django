from .models import Category

def categories_processor(request):
    """Make categories available in all templates"""
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}
