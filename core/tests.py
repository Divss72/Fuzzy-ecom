from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Category, Product, Order, OrderItem
from .views import fuzzy_search_products

User = get_user_model()

class FuzzySearchTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Rosette", slug="rosette")
        self.p1 = Product.objects.create(
            title="Echeveria Elegans",
            slug="echeveria-elegans",
            category=self.category,
            price=299.00,
            in_stock=True
        )
        self.p2 = Product.objects.create(
            title="Zebra Haworthia",
            slug="zebra-haworthia",
            category=self.category,
            price=249.00,
            in_stock=True
        )

    def test_fuzzy_exact_match(self):
        results = fuzzy_search_products("Echeveria")
        self.assertIn(self.p1, results)
        self.assertNotIn(self.p2, results)

    def test_fuzzy_misspelled_match(self):
        # Misspelled "echveria" should match "Echeveria Elegans"
        results = fuzzy_search_products("echveria")
        self.assertIn(self.p1, results)

        # Misspelled "hawortia" should match "Zebra Haworthia"
        results = fuzzy_search_products("hawortia")
        self.assertIn(self.p2, results)


class CartOperationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.category = Category.objects.create(name="Succulents", slug="succulents")
        self.p1 = Product.objects.create(
            title="Echeveria Elegans",
            slug="echeveria-elegans",
            category=self.category,
            price=200.00,
            in_stock=True
        )
        self.p2 = Product.objects.create(
            title="Zebra Haworthia",
            slug="zebra-haworthia",
            category=self.category,
            price=150.00,
            in_stock=True
        )

    def test_cart_totals(self):
        # Create order items
        item1 = OrderItem.objects.create(user=self.user, product=self.p1, quantity=2)
        item2 = OrderItem.objects.create(user=self.user, product=self.p2, quantity=3)

        # Create order
        order = Order.objects.create(user=self.user, ordered_date=timezone.now())
        order.items.add(item1, item2)

        # Totals verification
        # 2 * 200 = 400
        self.assertEqual(item1.get_total_item_price(), 400.00)
        # 3 * 150 = 450
        self.assertEqual(item2.get_total_item_price(), 450.00)
        # Total: 400 + 450 = 850
        self.assertEqual(order.get_total(), 850.00)
