import json
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(["POST"])
def register_order(request):
    order_data = request.data
    print(json.dumps(order_data, ensure_ascii=False, indent=4))
    with transaction.atomic():

        order = Order.objects.create(
            firstname=order_data["firstname"],
            lastname=order_data["lastname"],
            phonenumber=order_data["phonenumber"],
            address=order_data["address"]
        )

        for orderitem in order_data["products"]:
            product = Product.objects.get(id=orderitem["product"])
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=orderitem["quantity"]
            )

    return Response({"ok": "ok"},  status=status.HTTP_201_CREATED)
