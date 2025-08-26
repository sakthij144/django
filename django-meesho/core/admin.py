from django.contrib import admin
from .models import Category, Product, ProductImage, UserProfile, Cart, Order, OrderItem, Review, UserImage, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'title', 'description', 'is_primary', 'slug', 'name', 'price', 'discount_price', 'category', 'stock']
    verbose_name = 'Additional Image'
    verbose_name_plural = 'Additional Images'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_available', 'created_at']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_available']
    inlines = [ProductImageInline]
    
    # Exclude similar products
    exclude = ('similar_products',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'phone']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'quantity', 'price']
    extra = 0
    fields = ['product', 'quantity', 'price']
    verbose_name = 'Product'
    verbose_name_plural = 'Products in Order'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'get_product_names', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__username', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    actions = ['delete_selected_orders']
    
    def get_product_names(self, obj):
        return ", ".join([item.product.name for item in obj.items.all()])
    get_product_names.short_description = 'Products'
    
    def delete_selected_orders(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Successfully deleted {count} order(s).")
    delete_selected_orders.short_description = "Delete selected orders"
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'size', 'quantity', 'created_at']
    list_filter = ['size', 'created_at']
    search_fields = ['user__username', 'product__name']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price', 'discount_price', 'category', 'stock', 'title', 'is_primary', 'uploaded_at']
    list_editable = ['name', 'price', 'discount_price', 'category', 'stock', 'is_primary']
    list_filter = ['is_similar_product_image', 'is_primary', 'uploaded_at', 'category']
    search_fields = ['product__name', 'title', 'name']
    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'name', 'price', 'discount_price', 'category', 'stock')
        }),
        ('Image Details', {
            'fields': ('image', 'title', 'description', 'is_similar_product_image', 'is_primary', 'slug')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']
