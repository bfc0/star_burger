from rest_framework.serializers import ModelSerializer
from .models import Order, OrderLineSerializer


class OrderLineSerializer(ModelSerializer):
    class Meta:
        model = OrderLineSerializer
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderLineSerializer(
        many=True, allow_empty=False, source="orderlines")

    class Meta:
        model = Order
        fields = ["firstname", "lastname",
                  "phonenumber", "address", "products"]
