from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.http import JsonResponse
import json
from .models import Product, Category, Cart, Order, OrderItem, Review, UserProfile, Wishlist
from .forms import UserRegisterForm, ReviewForm, OrderForm, UserProfileForm

def home(request):
    # Get products from specific categories for the home page
    kitchen_products = Product.objects.filter(
        category__name__icontains='kitchen', 
        is_available=True
    )[:4]
    
    fashion_products = Product.objects.filter(
        category__name__icontains='fashion', 
        is_available=True
    )[:4]
    
    # Get all products for the trending section
    all_products = Product.objects.filter(is_available=True)[:8]
    
    context = {
        'products': all_products,
        'kitchen_products': kitchen_products,
        'fashion_products': fashion_products,
    }
    return render(request, 'core/home.html', context)

def shop(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True)
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__slug=category_filter)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'core/shop.html', context)

def shop_16_categories(request):
    """Display 16 categories with 3 products each"""
    categories = Category.objects.filter(is_active=True)[:16]
    
    context = {
        'categories': categories,
    }
    return render(request, 'core/shop_16_categories.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    print(f"Product: {product.name}, Category: {product.category.name}, Sizes: {product.FOOTWEAR_SIZE_CHOICES}")  # Debugging line
    print(f"Product: {product.name}, Category: {product.category.name}, Sizes: {product.FOOTWEAR_SIZE_CHOICES}")  # Debugging line
    reviews = Review.objects.filter(product=product)
    
    # Use the ManyToManyField for similar products
    similar_products = product.similar_products.filter(is_available=True)[:4]
    
    # If no similar products are manually selected, fall back to category-based similarity
    if not similar_products:
        similar_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]

    # Related products based on category
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Additional product images
    additional_images = product.additional_images.all()
    similar_product_images = additional_images.filter(is_similar_product_image=True)
    
    context = {
        'product': product,
        'reviews': reviews,
        'SIZE_CHOICES': Product.SIZE_CHOICES,
        'related_products': related_products,
        'similar_products': similar_products,
        'additional_images': additional_images,
        'similar_product_images': similar_product_images,
    }
    return render(request, 'core/product_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_view(request):
    """Custom logout view to handle user logout"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        
        # Check if size is required for this product category
        category_name = product.category.name.lower()
        # More comprehensive size detection for clothing items
        requires_size = any(keyword in category_name for keyword in [
            'shirt', 'kurti', 'kurt', 'top', 'blouse', 'dress', 'jeans', 'pant', 
            'trouser', 'jacket', 'coat', 'sweater', 'hoodie', 'sweatshirt'
        ])
        
        if requires_size and not size:
            messages.error(request, 'Please select a size for this product.')
            return redirect('product_detail', slug=product.slug)
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size if size else None,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'core/cart.html', context)

@login_required
def update_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        quantity = int(request.POST.get('quantity'))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        return redirect('cart')

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('shop')
    
    total = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.final_price,
                    size=cart_item.size
                )
            cart_items.delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation', order_id=order.order_id)
    else:
        form = OrderForm()
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    return render(request, 'core/checkout.html', context)

@login_required
def place_order(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart_item.total_price
            order.save()

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.final_price,
                size=cart_item.size
            )
            cart_item.delete()
            
            messages.success(request, f'Order for {cart_item.product.name} placed successfully!')
            return redirect('order_confirmation', order_id=order.order_id)
    else:
        form = OrderForm()
    
    context = {
        'cart_item': cart_item,  
        'total': cart_item.total_price,
        'form': form,
        'single_item': True,
    }
    return render(request, 'core/single_product_checkout.html', context)

@login_required
def single_product_checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    
    if quantity <= 0 or quantity > product.stock:
        messages.error(request, 'Invalid quantity selected.')
        return redirect('product_detail', slug=product.slug)
    
    total = product.final_price * quantity
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.final_price
            )
            
            messages.success(request, f'Order for {product.name} placed successfully!')
            return redirect('order_confirmation', order_id=order.order_id)
    else:
        form = OrderForm()
    
    context = {
        'product': product,
        'quantity': quantity,
        'total': total,
        'form': form,
    }
    return render(request, 'core/single_product_checkout.html', context)

@login_required
def place_order_direct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        from django.urls import reverse
        url = reverse('single_product_checkout', args=[product_id]) + f'?quantity={quantity}'
        return redirect(url)
    return redirect('product_detail', slug=product.slug)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'core/order_confirmation.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/my_orders.html', {'orders': orders})

@login_required
def cancel_order_item(request, order_item_id):
    """Cancel a specific order item"""
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__user=request.user)
    
    # Check if the order can be cancelled (only pending or confirmed orders)
    if order_item.order.status not in ['pending', 'confirmed']:
        messages.error(request, 'Cannot cancel item. Order is already shipped or delivered.')
        return redirect('my_orders')
    
    # Check if item is already cancelled
    if order_item.is_cancelled:
        messages.warning(request, 'This item is already cancelled.')
        return redirect('my_orders')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        order_item.cancel(reason)
        messages.success(request, f'{order_item.product.name} has been cancelled successfully.')
        
        # Check if all items in the order are cancelled
        all_cancelled = not order_item.order.items.filter(is_cancelled=False).exists()
        if all_cancelled:
            order_item.order.status = 'cancelled'
            order_item.order.save()
            messages.info(request, 'All items in this order have been cancelled. Order status updated to cancelled.')
        
        return redirect('my_orders')
    
    return render(request, 'core/cancel_item.html', {'order_item': order_item})

@login_required
def cancel_order(request, order_id):
    """Cancel an entire order"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Check if the order can be cancelled
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, 'Cannot cancel order. Order is already shipped or delivered.')
        return redirect('my_orders')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Cancel all items in the order
        for item in order.items.all():
            if not item.is_cancelled:
                item.cancel(reason)
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        messages.success(request, f'Order {order.order_id} has been cancelled successfully.')
        return redirect('my_orders')
    
    return render(request, 'core/cancel_order.html', {'order': order})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'core/profile.html', {'form': form})

@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f'{product.name} has been added to your wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    return redirect('product_detail', slug=product.slug)

@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product=product)
    wishlist_item.delete()
    messages.success(request, f'{product.name} has been removed from your wishlist.')
    return redirect('wishlist')

@login_required
def wishlist(request):
    """Display the user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'core/wishlist.html', context)

def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
            
            # Check if the request came from the orders page
            referer = request.META.get('HTTP_REFERER', '')
            if 'my_orders' in referer:
                return redirect('my_orders')
            else:
                return redirect('product_detail', slug=product.slug)
    
    # Redirect back to the appropriate page
    referer = request.META.get('HTTP_REFERER', '')
    if 'my_orders' in referer:
        return redirect('my_orders')
    else:
        return redirect('product_detail', slug=product.slug)

def api_add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        cart_count = Cart.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': f'{product.name} added to cart!'
        })
    
    return JsonResponse({'success': False, 'message': 'Authentication required'})
