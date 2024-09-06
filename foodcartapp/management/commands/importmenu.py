import json
import pprint
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from foodcartapp.models import ProductCategory, Product, Restaurant, RestaurantMenuItem


class Command(BaseCommand):
    help = "imports menu from specified folder"

    def add_arguments(self, parser):
        parser.add_argument("dirname", type=str)

    def handle(self, *args, **options):
        dirname = options["dirname"]

        products_file = dirname + "products.json"
        restaurants_file = dirname + "restaurants.json"
        saved_products, saved_restaurants = [], []

        try:
            with transaction.atomic():

                with open(products_file, "r") as file:
                    serialized_products = json.load(file)

                for product in serialized_products:

                    img_filename = dirname + "mediaf/" + product["img"]
                    with open(img_filename, "rb") as f:
                        img_content = f.read()

                        category, _ = ProductCategory.objects.get_or_create(
                            name=product["type"])

                        created_product, _ = Product.objects.update_or_create(
                            name=product["title"],
                            category=category,
                            defaults={
                                "price": product["price"],
                                "image": ContentFile(
                                    img_content, name=product["img"]),
                                "description": product["description"]
                            }
                        )
                        saved_products.append(created_product)

                with open(restaurants_file, "rb") as file:
                    restaurants = json.load(file)

                for restaurant in restaurants:
                    print(restaurant)
                    r, _ = Restaurant.objects.get_or_create(
                        name=restaurant["title"],
                        defaults={
                            "address": restaurant["address"],
                            "contact_phone": restaurant["contact_phone"],
                        }
                    )
                    saved_restaurants.append(r)

                for r in saved_restaurants:
                    for p in saved_products:
                        RestaurantMenuItem.objects.get_or_create(
                            restaurant=r,
                            product=p
                        )

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Error occurred: {e} "))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"directory imported successfully")
            )
