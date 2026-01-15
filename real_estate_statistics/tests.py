from django.test import Client, TestCase
from django.urls import reverse

from .models import RealEstateAd
from .utils import calculate_stats


class UtilsTest(TestCase):
    def test_calculate_stats_empty(self):
        qs = RealEstateAd.objects.none()
        stats = calculate_stats(qs)
        self.assertIsNone(stats)

    def test_calculate_stats_basic(self):
        RealEstateAd.objects.create(
            reference="1",
            co_ownership_charges=100,
            city="A",
            zip_code="01",
            department="01",
        )
        RealEstateAd.objects.create(
            reference="2",
            co_ownership_charges=200,
            city="A",
            zip_code="01",
            department="01",
        )
        RealEstateAd.objects.create(
            reference="3",
            co_ownership_charges=300,
            city="A",
            zip_code="01",
            department="01",
        )

        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)

        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["avg"], 200.0)
        self.assertEqual(stats["q10"], 120.0)
        self.assertEqual(stats["q90"], 280.0)

    def test_calculate_stats_one_item(self):
        RealEstateAd.objects.create(
            reference="1",
            co_ownership_charges=100,
            city="A",
            zip_code="01",
            department="01",
        )
        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)
        self.assertEqual(stats["q10"], 100.0)
        self.assertEqual(stats["q90"], 100.0)

    def test_calculate_stats_ignore_nulls(self):
        RealEstateAd.objects.create(
            reference="1",
            co_ownership_charges=100,
            city="A",
            zip_code="01",
            department="01",
        )
        RealEstateAd.objects.create(
            reference="2",
            co_ownership_charges=None,
            city="A",
            zip_code="01",
            department="01",
        )

        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)
        self.assertEqual(stats["count"], 1)
        self.assertEqual(stats["avg"], 100.0)


class StatsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        RealEstateAd.objects.create(
            reference="1",
            co_ownership_charges=100,
            city="Paris",
            zip_code="75001",
            department="75",
        )

    def test_stats_view_status(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
