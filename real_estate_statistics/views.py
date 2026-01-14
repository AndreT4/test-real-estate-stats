from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.views.generic import TemplateView
import requests

from .models import RealEstateAd
from .utils import calculate_stats

class StatsView(TemplateView):
    template_name = 'real_estate_statistics/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        city = self.request.GET.get('city')
        zip_code = self.request.GET.get('zip_code')
        department = self.request.GET.get('department')
        
        qs = RealEstateAd.objects.filter(co_ownership_charges__isnull=False)
        
        if city:
            qs = qs.filter(city__icontains=city)
        if zip_code:
            qs = qs.filter(zip_code=zip_code)
        if department:
            qs = qs.filter(department=department)
            
        context['filters'] = {
            'city': city,
            'zip_code': zip_code,
            'department': department
        }
        
        if qs.exists() and (city or zip_code or department): 
            context['stats'] = calculate_stats(qs)
        elif any([city, zip_code, department]):
             context['error'] = "No data found for these criteria."
             
        return context

class ImportAdView(View):
    template_name = 'real_estate_statistics/import.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        url = request.POST.get('url')
        if not url:
            messages.error(request, "Please provide a URL")
            return redirect('import_ad')
            
        try:
            # Parse ID from URL BienIci URL
            parts = url.split('?')[0].split('/')
            potential_id = parts[-1] 
            
            api_url = f"https://www.bienici.com/realEstateAd.json?id={potential_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
            }
            resp = requests.get(api_url, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                ref = data.get('reference', potential_id)
                price = data.get('price')
                city = data.get('city')
                zip_code = data.get('postalCode')
                
                dept = zip_code[:2] if zip_code else ''
                charges = data.get('condominiumExpenses')
                surface = data.get('surfaceArea')
                
                RealEstateAd.objects.update_or_create(
                    reference=ref,
                    defaults={
                        'city': city,
                        'zip_code': zip_code,
                        'department': dept,
                        'co_ownership_charges': charges,
                    }
                )
                
                if charges is None:
                    messages.warning(request, f"Ad {ref} imported, but it has no co-ownership charges data.")
                else:
                    messages.success(request, f"Ad {ref} imported successfully!")
            else:
                messages.error(request, "Failed to fetch ad from BienIci API")
                
        except Exception as e:
             messages.error(request, f"Error: {e}")
             
        return redirect('stats')

class AutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        field = request.GET.get('field', '')
        
        if len(q) < 3:
            return JsonResponse([], safe=False)
            
        results = []
        if field == 'city':
            results = list(RealEstateAd.objects.filter(city__icontains=q)
                           .values_list('city', flat=True)
                           .distinct().order_by('city')[:10])
        elif field == 'department':
            results = list(RealEstateAd.objects.filter(department__startswith=q)
                           .values_list('department', flat=True)
                           .distinct().order_by('department')[:10])
                           
        return JsonResponse(results, safe=False)
