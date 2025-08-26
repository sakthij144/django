from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop-16-categories/', views.shop_16_categories, name='shop_16_categories'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/<int:cart_id>/', views.place_order, name='place_order'),
    path('place-order-direct/<int:product_id>/', views.place_order_direct, name='place_order_direct'),
    path('single-product-checkout/<int:product_id>/', views.single_product_checkout, name='single_product_checkout'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('profile/', views.profile, name='profile'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('api/add-to-cart/', views.api_add_to_cart, name='api_add_to_cart'),
    path('cancel/order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('cancel/item/<int:order_item_id>/', views.cancel_order_item, name='cancel_order_item'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
