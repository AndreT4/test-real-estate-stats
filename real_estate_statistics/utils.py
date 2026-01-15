from django.db.models import Avg
from .models import RealEstateAd
from statistics import quantiles


def calculate_stats(qs):
    """
    Calculate average, q10, and q90 for a given queryset of ads.
    Returns a dict with count, avg, q10, q90.
    """
    if not qs.exists():
        return None

    avg_charges = qs.aggregate(avg=Avg("co_ownership_charges"))["avg"]

    values = list(
        qs.filter(co_ownership_charges__isnull=False)
        .values_list("co_ownership_charges", flat=True)
        .order_by("co_ownership_charges")
    )

    n = len(values)

    if n >= 2:
        percentiles = quantiles(values, n=10, method="inclusive")
        q10 = percentiles[0]
        q90 = percentiles[-1]
    elif n == 1:
        q10 = values[0]
        q90 = values[0]
    else:
        q10 = 0
        q90 = 0

    return {
        "count": n,
        "avg": round(avg_charges, 2) if avg_charges else 0,
        "q10": round(q10, 2),
        "q90": round(q90, 2),
    }
