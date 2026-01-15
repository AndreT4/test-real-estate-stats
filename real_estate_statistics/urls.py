from django.urls import path

from .api_views import AutocompleteAPIView, ImportAdAPIView, StatsAPIView
from .views import ImportAdView, StatsView

urlpatterns = [
    path("", StatsView.as_view(), name="stats"),
    path("import/", ImportAdView.as_view(), name="import_ad"),
    path("api/stats/", StatsAPIView.as_view(), name="api_stats"),
    path("api/import/", ImportAdAPIView.as_view(), name="api_import"),
    path("autocomplete/", AutocompleteAPIView.as_view(), name="autocomplete"),
]
