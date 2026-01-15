from rest_framework import serializers
from .models import RealEstateAd


class RealEstateAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateAd
        fields = [
            "id",
            "reference",
            "city",
            "zip_code",
            "department",
            "co_ownership_charges",
        ]
