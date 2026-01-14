from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import RealEstateAd
from .utils import calculate_stats
from .views import AutocompleteView

class UtilsTest(TestCase):
    def test_calculate_stats_empty(self):
        qs = RealEstateAd.objects.none()
        stats = calculate_stats(qs)
        self.assertIsNone(stats)

    def test_calculate_stats_basic(self):
        RealEstateAd.objects.create(reference='1', co_ownership_charges=100, city='A', zip_code='01', department='01')
        RealEstateAd.objects.create(reference='2', co_ownership_charges=200, city='A', zip_code='01', department='01')
        RealEstateAd.objects.create(reference='3', co_ownership_charges=300, city='A', zip_code='01', department='01')
        
        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)
        
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['avg'], 200.0)
        self.assertEqual(stats['q10'], 120.0)
        self.assertEqual(stats['q90'], 280.0)

    def test_calculate_stats_one_item(self):
        RealEstateAd.objects.create(reference='1', co_ownership_charges=100, city='A', zip_code='01', department='01')
        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)
        self.assertEqual(stats['q10'], 100.0)
        self.assertEqual(stats['q90'], 100.0)

    def test_calculate_stats_ignore_nulls(self):
        RealEstateAd.objects.create(reference='1', co_ownership_charges=100, city='A', zip_code='01', department='01')
        RealEstateAd.objects.create(reference='2', co_ownership_charges=None, city='A', zip_code='01', department='01')
        
        qs = RealEstateAd.objects.all()
        stats = calculate_stats(qs)
        self.assertEqual(stats['count'], 1)
        self.assertEqual(stats['avg'], 100.0)

class StatsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        RealEstateAd.objects.create(reference='1', co_ownership_charges=100, city='Paris', zip_code='75001', department='75')
        RealEstateAd.objects.create(reference='2', co_ownership_charges=200, city='Lyon', zip_code='69001', department='69')

    def test_stats_view_status(self):
        response = self.client.get(reverse('stats'))
        self.assertEqual(response.status_code, 200)
        
    def test_stats_view_filter_city(self):
        response = self.client.get(reverse('stats'), {'city': 'Paris'})
        self.assertEqual(response.context['stats']['count'], 1)
        self.assertEqual(response.context['filters']['city'], 'Paris')

    def test_stats_view_no_data(self):
        response = self.client.get(reverse('stats'), {'city': 'Unknown'})
        self.assertIsNone(response.context.get('stats'))
        self.assertIsNotNone(response.context.get('error'))

class AutocompleteViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        RealEstateAd.objects.create(reference='1', city='Bordeaux', zip_code='33000', department='33')
        RealEstateAd.objects.create(reference='2', city='Bormes', zip_code='83230', department='83')

    def test_autocomplete_city(self):
        request = self.factory.get('/autocomplete/', {'q': 'Bor', 'field': 'city'})
        view = AutocompleteView.as_view()
        response = view(request)
        content = response.content.decode()
        self.assertIn('Bordeaux', content)
        self.assertIn('Bormes', content)

class ImportAdViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.import_url = reverse('import_ad')

    @patch('requests.get')
    def test_import_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'reference': 'REF123',
            'city': 'Paris',
            'postalCode': '75010',
            'condominiumExpenses': 150.0,
            'surfaceArea': 50 # Check it is not considered
        }
        mock_get.return_value = mock_response

        url_to_add = 'https://www.bienici.com/annonce/vente/paris/REF123'
        response = self.client.post(self.import_url, {'url': url_to_add})
        
        self.assertRedirects(response, reverse('stats'))
        
        ad = RealEstateAd.objects.get(reference='REF123')
        self.assertEqual(ad.city, 'Paris')
        self.assertEqual(ad.co_ownership_charges, 150.0)
