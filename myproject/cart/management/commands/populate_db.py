from django.core.management.base import BaseCommand
from faker import Faker
from cart.models import Product, CartItem
from reviews.models import Restaurant, Review
from django.contrib.auth import get_user_model
import random
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with fake data for products, cart items, restaurants, and reviews'

    def handle(self, *args, **kwargs):
        fake = Faker()

        product_photos_folder = os.path.join('media', 'products')
        product_photos = [
            os.path.join('products', file)
            for file in os.listdir(product_photos_folder)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

        if not product_photos:
            self.stdout.write(self.style.ERROR('No product photos found in the folder'))
            return
        

        restaurant_photos_folder = os.path.join('media', 'restaurants')
        restaurant_photos = [
            os.path.join('restaurants', file)
            for file in os.listdir(restaurant_photos_folder)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

        if not restaurant_photos:
            self.stdout.write(self.style.ERROR('No restaurant photos found in the folder'))
            return

        # Create fake products
        products = []
        for _ in range(200):  # Create 200 products
            product = Product.objects.create(
                name=fake.word().capitalize(),
                price=fake.random_number(digits=5, fix_len=True) + fake.random_number(digits=2) / 100,  # Random price
                description=fake.text(max_nb_chars=200),
                photo=random.choice(product_photos),  # Use a default image path or handle image uploads differently
                category=fake.word().capitalize()
            )
            products.append(product)

        # Create fake restaurants
        restaurants = []
        for _ in range(200):  # Create 200 restaurants
            restaurant = Restaurant.objects.create(
                name=fake.company(),
                description=fake.text(max_nb_chars=200),
                address=fake.address(),
                owner=random.choice(User.objects.all()),  # Randomly assign an owner from existing users
                photo=random.choice(restaurant_photos)  # Use a default image path
            )
            restaurants.append(restaurant)

        # Create fake reviews
        for restaurant in restaurants:
            for _ in range(random.randint(1, 7)):  # Each restaurant can have 1 to 7 reviews
                Review.objects.create(
                    user=random.choice(User.objects.all()),  # Randomly select a user
                    restaurant=restaurant,
                    rating=random.randint(1, 5),  # Random rating between 1 and 5
                    comment=fake.text(max_nb_chars=300),  # Random comment
                    is_approved=random.choice([True, False])  # Randomly set approval status
                )

        # Create fake cart items
        users = User.objects.all()  # Get all users
        for user in users:
            for _ in range(random.randint(1, 5)):  # Each user can have 1 to 5 cart items
                CartItem.objects.create(
                    user=user,
                    product=random.choice(products),  # Randomly select a product
                    quantity=random.randint(1, 10)  # Random quantity between 1 and 50
                )

        self.stdout.write(self.style.SUCCESS('Database populated with fake data for products, cart items, restaurants, and reviews!'))
