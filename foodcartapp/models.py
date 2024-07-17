from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        unique=True
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=250,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(total=Sum(
            F("orderlines__price")*F("orderlines__quantity")
        ))


class Order(models.Model):
    STATUSES = [
        (0, 'новый'),
        (1, 'готовится'),
        (2, 'доставляется'),
        (3, 'исполнен'),
    ]

    firstname = models.CharField("имя", max_length=50)
    lastname = models.CharField("фамилия", max_length=50)
    phonenumber = PhoneNumberField(
        verbose_name="номер телефона", db_index=True)
    address = models.CharField("адрес доставки", max_length=200)
    created = models.DateTimeField("создан", auto_now_add=True, db_index=True)
    updated = models.DateTimeField("изменен", auto_now=True)
    status = models.IntegerField(
        'Статус', choices=STATUSES, default=0, db_index=True)

    objects = OrderManager()

    class Meta:
        ordering = ("-created",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"Заказ {self.id}"


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, related_name="orderlines", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="orderlines", on_delete=models.CASCADE, verbose_name="товар")
    price = models.DecimalField("цена",
                                max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField("количество",
                                           default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ["order", "product"]

    def __str__(self):
        return f"Товар {self.id}"
