import random
from django.core.management.base import BaseCommand
from faker import Faker
from products.models import Category, Brand, HardwareProduct, SoftwareProduct, ProductReview, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Populate the database with sample product data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Delete existing data (optional - uncomment if you want to clear before populating)
        # self.stdout.write('Deleting existing data...')
        # ProductReview.objects.all().delete()
        # ProductImage.objects.all().delete()
        # HardwareProduct.objects.all().delete()
        # SoftwareProduct.objects.all().delete()
        # Brand.objects.all().delete()
        # Category.objects.all().delete()

        categories = []
        for _ in range(5):
            cat = Category.objects.create(
                name=fake.unique.word().capitalize(),
                description=fake.text(max_nb_chars=100)
            )
            categories.append(cat)

        brands = []
        for _ in range(5):
            brand = Brand.objects.create(
                name=fake.company(),
                website=fake.url()
            )
            brands.append(brand)

        # Create some test users for reviews
        users = []
        for i in range(3):
            # Using get_or_create properly (was creating unusable password)
            user, created = User.objects.get_or_create(
                username=f"user{i}", 
                defaults={
                    "email": f"user{i}@example.com"
                }
            )
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)

        # Create hardware products
        for _ in range(20):
            category = random.choice(categories)
            brand = random.choice(brands)
            
            product_name = fake.unique.word().capitalize() + " Pro"
            
            hp = HardwareProduct.objects.create(
                name=product_name,
                sku=fake.unique.bothify(text='???-#####'),
                description=fake.text(),
                price=random.randint(500, 2500),
                sale_price=random.choice([None, random.randint(400, 1200)]),
                category=category,
                brand=brand,
                featured=random.choice([True, False]),
                status=random.choice(['draft', 'published', 'out_of_stock']),
                product_type='hardware',  # Make sure product_type is set
                release_date=fake.date_between(start_date='-2y', end_date='today'),
                quantity=random.randint(0, 50),
                warranty_months=random.randint(6, 24),
                weight=random.uniform(1.0, 3.0),
                dimensions="{}x{}x{}".format(random.randint(20, 40), random.randint(15, 30), random.randint(1, 5)),
                color=random.choice(['Black', 'White', 'Silver', 'Gray']),
                condition=random.choice(['new', 'refurbished', 'used']),
                processor=random.choice(['Intel i5', 'Intel i7', 'Ryzen 5']),
                memory=random.choice(['8GB', '16GB', '32GB']),
                storage=random.choice(['256GB SSD', '512GB SSD', '1TB HDD']),
                display=random.choice(['13"', '14"', '15.6"', '17"']),
                battery_life=f"{random.randint(6, 12)} hours",
                camera='720p HD',
                operating_system=random.choice(['Windows 11', 'Ubuntu 22.04', 'macOS Ventura'])
            )
            
            # Add product images
            for i in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    hardware_product=hp,
                    image=f"products/placeholder_{random.randint(1, 5)}.jpg",  # Placeholder images
                    alt_text=f"{product_name} image {i+1}",
                    is_primary=(i == 0)  # First image is primary
                )

            # Add product reviews
            for _ in range(random.randint(1, 5)):
                ProductReview.objects.create(
                    hardware_product=hp,
                    user=random.choice(users),
                    rating=random.randint(1, 5),
                    title=fake.sentence(nb_words=4),
                    comment=fake.text(),
                    verified_purchase=random.choice([True, False])
                )

        # Create software products
        for _ in range(15):
            category = random.choice(categories)
            brand = random.choice(brands)
            
            product_name = fake.unique.word().capitalize() + " Software"
            
            sp = SoftwareProduct.objects.create(
                name=product_name,
                sku=fake.unique.bothify(text='SW-#####'),
                description=fake.text(),
                price=random.randint(10, 200),
                sale_price=random.choice([None, random.randint(5, 99)]),
                category=category,
                brand=brand,
                featured=random.choice([True, False]),
                status=random.choice(['draft', 'published']),
                product_type='software',  # Make sure product_type is set
                release_date=fake.date_between(start_date='-2y', end_date='today'),
                license_type=random.choice(['perpetual', 'subscription', 'freemium', 'open_source']),
                version=fake.random_element(elements=('2021', '2022', '2023', '2024')),
                edition=random.choice(['standard', 'professional', 'enterprise']),
                platform=random.choice(['Windows', 'Mac', 'Linux']),
                download_link=fake.url(),
                activation_key_required=random.choice([True, False]),
                subscription_period=random.choice([None, 6, 12, 24]),
                system_requirements="4GB RAM, 10GB Disk Space"
            )
            
            # Add product images
            for i in range(random.randint(1, 2)):
                ProductImage.objects.create(
                    software_product=sp,
                    image=f"products/software_placeholder_{random.randint(1, 3)}.jpg",  # Placeholder images
                    alt_text=f"{product_name} image {i+1}",
                    is_primary=(i == 0)  # First image is primary
                )

            # Add product reviews
            for _ in range(random.randint(1, 3)):
                ProductReview.objects.create(
                    software_product=sp,
                    user=random.choice(users),
                    rating=random.randint(2, 5),
                    title=fake.sentence(nb_words=4),
                    comment=fake.text(),
                    verified_purchase=True
                )

        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))
