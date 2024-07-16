from rest_framework.serializers import ModelSerializer
from django.db import transaction
from .models import Order, OrderLine, Product


class OrderLineSerializer(ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderLineSerializer(
        many=True, allow_empty=False, source="orderlines", write_only=True)

    class Meta:
        model = Order
        fields = ["firstname", "lastname",
                  "phonenumber", "address", "products"]

    def create(self, validated_data):
        orderlines = validated_data.pop("orderlines")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for orderline in orderlines:
                product = Product.objects.get(id=orderline["product"].id)
                OrderLine.objects.create(
                    order=order, price=product.price, **orderline)
            return order
