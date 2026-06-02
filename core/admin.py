# core/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage, CustomOrder, Order, OrderItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(CustomOrder)
admin.site.register(Order)
admin.site.register(OrderItem)

