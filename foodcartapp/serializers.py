from rest_framework.serializers import ModelSerializer, ReadOnlyField, CharField

from django.db import transaction
from .models import Order, OrderLine, Product


class OrderLineSerializer(ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderLineSerializer(
        many=True, allow_empty=False, source="orderlines", write_only=True)
    total = ReadOnlyField()
    id = ReadOnlyField()
    status_name = ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ("id", "firstname", "lastname",
                  "phonenumber", "address", "products", "total", "status", "status_name")

    @transaction.atomic
    def create(self, validated_data):
        orderlines = validated_data.pop("orderlines")
        order = Order.objects.create(**validated_data)
        for orderline in orderlines:
            product = Product.objects.get(id=orderline["product"].id)
            OrderLine.objects.create(
                order=order, price=product.price, **orderline)
        return order
