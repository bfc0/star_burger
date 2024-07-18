from django.db import models


class Location(models.Model):
    address = models.CharField(max_length=250, db_index=True, unique=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"location {self.id} ({self.address})"
