from django.urls import path, include
from .views import StatsView, ImportAdView
from .api_views import StatsAPIView, ImportAdAPIView, AutocompleteAPIView


urlpatterns = [
    path('', StatsView.as_view(), name='stats'),
    path('import/', ImportAdView.as_view(), name='import_ad'),
    
    path('api/stats/', StatsAPIView.as_view(), name='api_stats'),
    path('api/import/', ImportAdAPIView.as_view(), name='api_import'),
    path('autocomplete/', AutocompleteAPIView.as_view(), name='autocomplete'),
]
