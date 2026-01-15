import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RealEstateAd
from .serializers import RealEstateAdSerializer
from .utils import calculate_stats


class StatsAPIView(APIView):
    """
    API endpoint to retrieve statistics.
    """

    def get(self, request):
        city = request.query_params.get("city")
        zip_code = request.query_params.get("zip_code")
        department = request.query_params.get("department")

        qs = RealEstateAd.objects.filter(co_ownership_charges__isnull=False)

        if city:
            qs = qs.filter(city__icontains=city)
        if zip_code:
            qs = qs.filter(zip_code=zip_code)
        if department:
            qs = qs.filter(department=department)

        stats = calculate_stats(qs)

        if stats:
            return Response(stats)
        else:
            return Response(
                {"error": "No data found for these criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ImportAdAPIView(APIView):
    """
    API endpoint to import an ad from a URL.
    """

    def post(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "Please provide a URL"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Parse ID from URL BienIci URL logic (simplified from original view)
            parts = url.split("?")[0].split("/")
            potential_id = parts[-1]

            api_url = f"https://www.bienici.com/realEstateAd.json?id={potential_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
            }
            resp = requests.get(api_url, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                ref = data.get("reference", potential_id)
                price = data.get("price")
                city = data.get("city")
                zip_code = data.get("postalCode")

                dept = zip_code[:2] if zip_code else ""
                charges = data.get("condominiumExpenses")

                ad, created = RealEstateAd.objects.update_or_create(
                    reference=ref,
                    defaults={
                        "city": city,
                        "zip_code": zip_code,
                        "department": dept,
                        "co_ownership_charges": charges,
                    },
                )

                msg = f"Ad {ref} imported successfully!"
                if charges is None:
                    msg += " Warning: No co-ownership charges data."

                serializer = RealEstateAdSerializer(ad)
                return Response(
                    {"message": msg, "ad": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Failed to fetch ad from BienIci API"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AutocompleteAPIView(APIView):
    """
    API endpoint for autocomplete suggestions.
    """

    def get(self, request):
        q = request.query_params.get("q", "")
        field = request.query_params.get("field", "")

        if len(q) < 3:
            return Response([])

        results = []
        if field == "city":
            results = list(
                RealEstateAd.objects.filter(city__icontains=q)
                .values_list("city", flat=True)
                .distinct()
                .order_by("city")[:10]
            )

        return Response(results)
