
from django.urls import path
from django.contrib.auth import views as auth_views # Import this
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('custom-order/', views.custom_order, name='custom_order'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
     # Auth URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
]

# Add this inside urlpatterns
