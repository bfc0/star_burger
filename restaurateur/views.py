from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db import connection, reset_queries

from locations.service import CoordinateService
from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from restaurateur.service import get_restaraunts_can_handle_order


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(
            restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    restaurants = Restaurant.objects.prefetch_related(
        Prefetch('menu_items', queryset=RestaurantMenuItem.objects.filter(
            availability=True).select_related("product"))
    )

    availability = {r: {item.product.id for item in r.menu_items.all()}
                    for r in restaurants}

    orders = Order.objects.exclude(
        status=Order.STATUS_COMPLETED).order_by("status", "-created")\
        .prefetch_related("orderlines__product").select_related("assigned_restaurant")

    order_addresses = {order.address for order in orders}
    restaurant_addresses = {r.address for r in restaurants}
    all_addresses = order_addresses | restaurant_addresses
    coordservice = CoordinateService(all_addresses)

    for order in orders:
        products_required = {
            line.product.id for line in order.orderlines.all()}

        restaurants_can_handle = get_restaraunts_can_handle_order(
            availability, products_required, coordservice, order)

        order.available_restaurants = [
            {
                "name": f"{name} {distance}km" if distance is not None else str(name),
                "id": restaurant_id,
            } for restaurant_id, name, distance in restaurants_can_handle
        ]

    return render(request, template_name='order_items.html', context={
        "order_items": orders
    })


def crashing_view(request):
    raise
