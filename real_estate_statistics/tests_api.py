from unittest.mock import MagicMock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import RealEstateAd


class RealEstateAdAPITests(APITestCase):
    def setUp(self):
        self.ad1 = RealEstateAd.objects.create(
            reference="REF001",
            city="Paris",
            zip_code="75001",
            department="75",
            co_ownership_charges=100,
        )
        self.ad2 = RealEstateAd.objects.create(
            reference="REF002",
            city="Lyon",
            zip_code="69001",
            department="69",
            co_ownership_charges=200,
        )

    def test_get_stats(self):
        url = reverse("api_stats")
        response = self.client.get(url, {"city": "Paris"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["avg"], 100.0)

    @patch("requests.get")
    def test_import_ad(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "reference": "REF123",
            "city": "Nice",
            "postalCode": "06000",
            "condominiumExpenses": 300.0,
        }
        mock_get.return_value = mock_response

        url = reverse("api_import")
        data = {"url": "https://www.bienici.com/realEstateAd.json?id=REF123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RealEstateAd.objects.get(reference="REF123").city, "Nice")
