from .models import Order

def cart_count(request):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            count = sum(item.quantity for item in order.items.all())
            return {'cart_count': count}
        except Order.DoesNotExist:
            pass
    return {'cart_count': 0}
