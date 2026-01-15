from django.db import models


class RealEstateAd(models.Model):
    """Represent an ad of a real estate"""

    reference = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    department = models.CharField(max_length=10)
    co_ownership_charges = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.reference} - {self.city}"
