from django.urls import path
from .views import StatsView, ImportAdView, AutocompleteView

urlpatterns = [
    path('', StatsView.as_view(), name='stats'),
    path('import/', ImportAdView.as_view(), name='import_ad'),
    path('autocomplete/', AutocompleteView.as_view(), name='autocomplete'),
]
