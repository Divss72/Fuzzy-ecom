from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CustomOrder

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Product, OrderItem, Order # Import your new models!
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        return redirect('home')

    # Calculate total price
    total_price = sum(item.total_price() for item in cart_items)
    
    # Razorpay needs amount in Paise (100 paise = 1 Rupee)
    # So ₹500 becomes 50000
    amount_in_paise = int(total_price * 100)

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Order
    payment_order = client.order.create({
        'amount': amount_in_paise, 
        'currency': 'INR', 
        'payment_capture': '1' 
    })

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'api_key': settings.RAZORPAY_KEY_ID,
        'order_id': payment_order['id'],
        'amount': amount_in_paise, # needed for the script
    }
    return render(request, 'checkout.html', context)

@csrf_exempt # We use csrf_exempt here because Razorpay sends a POST request back to us
def payment_success(request):
    if request.method == "POST":
        # In a real app, you would verify the signature here
        # For now, let's assume success, clear the cart, and show a success message
        
        # Clear the user's cart
        CartItem.objects.filter(user=request.user).delete()
        
        return render(request, 'success.html')
    return redirect('home')

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Create or get the OrderItem
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    
    # Get the unfinished order for this user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs[0]
        # Check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            print("Quantity updated")
        else:
            order.items.add(order_item)
            print("Added to order")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        print("New order created")
        
    return redirect("product_detail", slug=slug)

def home(request):
    products = Product.objects.filter(in_stock=True)[:24]
    return render(request, 'core/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'core/product_detail.html', {'product': product})

def custom_order(request):
    if request.method == 'POST':
        # handle form submission
        pass
    return render(request, 'core/custom_order.html')

@login_required
def cart_view(request):
    try:
        # Get the unfinished order for the current user
        order = Order.objects.get(user=request.user, ordered=False)
        context = {'order': order}
    except ObjectDoesNotExist:
        # If no order exists, show empty cart
        context = {'order': None}
        
    return render(request, 'core/cart.html', context)
def checkout(request):
    return render(request, 'core/checkout.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log them in immediately
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})