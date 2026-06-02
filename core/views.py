import difflib
import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Product, Category, Order, OrderItem, CustomOrder
from .forms import CustomOrderForm

def fuzzy_search_products(query, threshold=0.5):
    query = query.lower().strip()
    if not query:
        return Product.objects.filter(in_stock=True)
        
    products = Product.objects.filter(in_stock=True)
    results = []
    
    for product in products:
        title = product.title.lower()
        desc = product.description.lower() if product.description else ''
        category_name = product.category.name.lower() if product.category else ''
        
        # Calculate similarity score
        score = 0
        
        # 1. Exact match / substring match
        if query in title:
            score += 1.0 + (len(query) / len(title)) # Bias shorter exact matches
        elif query in category_name:
            score += 0.8
        elif query in desc:
            score += 0.4
            
        # 2. Fuzzy match word-by-word
        query_words = query.split()
        title_words = title.split()
        
        word_scores = []
        for qw in query_words:
            best_word_score = 0
            for tw in title_words:
                ratio = difflib.SequenceMatcher(None, qw, tw).ratio()
                if ratio > best_word_score:
                    best_word_score = ratio
            word_scores.append(best_word_score)
            
        if word_scores:
            avg_word_score = sum(word_scores) / len(word_scores)
            score += avg_word_score
            
        if score >= threshold:
            results.append((product, score))
            
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in results]

def home(request):
    query = request.GET.get('q', '')
    if query:
        products = fuzzy_search_products(query)
    else:
        products = Product.objects.filter(in_stock=True)[:24]
    return render(request, 'core/home.html', {'products': products, 'query': query})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def cart_view(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {'order': order}
    except ObjectDoesNotExist:
        context = {'order': None}
    return render(request, 'core/cart.html', context)

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f"Updated {product.title} quantity to {order_item.quantity} in your cart.")
        else:
            order.items.add(order_item)
            messages.success(request, f"Added {product.title} to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, f"Created cart and added {product.title}.")
        
    return redirect("cart_view")

@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.warning(request, f"Removed {product.title} from your cart.")
        else:
            messages.info(request, f"{product.title} was not in your cart.")
    else:
        messages.info(request, "You do not have an active cart.")
    return redirect("cart_view")

@login_required
def decrease_quantity(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f"Decreased {product.title} quantity to {order_item.quantity}.")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.warning(request, f"Removed {product.title} from your cart.")
        else:
            messages.info(request, f"{product.title} was not in your cart.")
    else:
        messages.info(request, "You do not have an active cart.")
    return redirect("cart_view")

@login_required
def checkout(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order.")
        return redirect('home')
        
    if not order.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    total_price = order.get_total()
    amount_in_paise = int(total_price * 100)

    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        payment_order = client.order.create({
            'amount': amount_in_paise, 
            'currency': 'INR', 
            'payment_capture': '1' 
        })
        razorpay_order_id = payment_order['id']
    except Exception as e:
        # Fallback for offline testing / invalid keys
        razorpay_order_id = f"fake_order_{int(timezone.now().timestamp())}"

    context = {
        'order': order,
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_amount': amount_in_paise,
        'currency': 'INR',
    }
    return render(request, 'core/checkout.html', context)

@csrf_exempt
@login_required
def payment_success(request):
    if request.method == "POST":
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            order.ordered = True
            order.ordered_date = timezone.now()
            for item in order.items.all():
                item.ordered = True
                item.save()
            order.save()
            messages.success(request, "Payment successful! Your order has been placed.")
        except ObjectDoesNotExist:
            messages.error(request, "Could not find active order to finalize.")
        
        return render(request, 'core/success.html')
    return redirect('home')

def custom_order(request):
    if request.method == 'POST':
        form = CustomOrderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your custom succulent request has been submitted successfully!")
            return redirect('custom_order')
    else:
        form = CustomOrderForm()
    return render(request, 'core/custom_order.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Fuzzy Succulents!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})