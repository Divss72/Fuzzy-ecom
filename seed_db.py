import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuzzy.settings')
django.setup()

from core.models import Category, Product, ProductImage

def seed():
    # Clear existing data
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()

    print("Seeding database...")

    # Create Categories
    c_rosette = Category.objects.create(name="Rosette Succulents", slug="rosette-succulents")
    c_cacti = Category.objects.create(name="Cacti", slug="cacti")
    c_aloe = Category.objects.create(name="Aloe Varieties", slug="aloe-varieties")
    c_hanging = Category.objects.create(name="Hanging Succulents", slug="hanging-succulents")

    # Create Products
    p1 = Product.objects.create(
        title="Echeveria Elegans",
        slug="echeveria-elegans",
        category=c_rosette,
        description="A beautiful, tight-rosette succulent with pale blue-green leaves that blush pink at the tips under bright sunlight. Very easy to care for and perfect for window sills.",
        price=299.00,
        in_stock=True,
        is_customizable=True
    )
    ProductImage.objects.create(product=p1, image="products/echeveria_elegans.png")

    p2 = Product.objects.create(
        title="Zebra Haworthia",
        slug="zebra-haworthia",
        category=c_aloe,
        description="Features striking, dark green pointed leaves adorned with horizontal white stripes resembling a zebra. Extremely hardy and tolerant of lower light conditions.",
        price=249.00,
        in_stock=True,
        is_customizable=False
    )
    ProductImage.objects.create(product=p2, image="products/zebra_haworthia.png")

    p3 = Product.objects.create(
        title="Blue Echeveria",
        slug="blue-echeveria",
        category=c_rosette,
        description="A rosette succulent displaying dusty blue leaves with subtle red edges. Perfect for succulent bowls.",
        price=319.00,
        in_stock=True,
        is_customizable=True
    )
    ProductImage.objects.create(product=p3, image="products/echeveria_elegans.png")

    p4 = Product.objects.create(
        title="Striated Haworthia",
        slug="striated-haworthia",
        category=c_aloe,
        description="A variation of the Haworthia featuring wider striped ridges and thick, water-storing leaves.",
        price=279.00,
        in_stock=True,
        is_customizable=False
    )
    ProductImage.objects.create(product=p4, image="products/zebra_haworthia.png")

    p5 = Product.objects.create(
        title="Golden Barrel Cactus",
        slug="golden-barrel-cactus",
        category=c_cacti,
        description="A classic globe-shaped cactus covered in beautiful golden-yellow spines. Highly popular for desert themed gardens.",
        price=450.00,
        in_stock=True,
        is_customizable=False
    )

    p6 = Product.objects.create(
        title="String of Pearls",
        slug="string-of-pearls",
        category=c_hanging,
        description="A cascading succulent with pea-like green beads dangling from thin stems. Looks magnificent in hanging pots.",
        price=399.00,
        in_stock=True,
        is_customizable=False
    )

    print(f"Successfully seeded database! Categories: {Category.objects.count()}, Products: {Product.objects.count()}")

if __name__ == "__main__":
    seed()
