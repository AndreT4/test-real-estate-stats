from django.views.generic import TemplateView

class StatsView(TemplateView):
    template_name = 'real_estate_statistics/stats.html'

class ImportAdView(TemplateView):
    template_name = 'real_estate_statistics/import.html'
