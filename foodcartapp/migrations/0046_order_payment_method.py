# Generated by Django 3.2.15 on 2024-07-17 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20240717_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.IntegerField(choices=[(0, 'наличные'), (1, 'электронно')], db_index=True, default=0, verbose_name='оплата'),
        ),
    ]
