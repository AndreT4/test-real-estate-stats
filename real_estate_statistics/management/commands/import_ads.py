import csv
from django.core.management.base import BaseCommand
from real_estate_statistics.models import RealEstateAd


class Command(BaseCommand):
    help = "Import ads from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        self.stdout.write(f"Importing from {csv_file}...")

        real_estate_ads_to_create = []

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip if no charges founds
                charges_str = row.get("CONDOMINIUM_EXPENSES")
                if not charges_str or charges_str.strip() == "":
                    continue
                charges = float(charges_str)

                # Reference logic
                parts = row.get("AD_URLS", "").split("?")[0].split("/")
                potential_id = parts[-1]
                ref = potential_id
                if not ref:
                    continue

                real_estate_ad = RealEstateAd(
                    reference=ref,
                    city=row.get("CITY", ""),
                    zip_code=row.get("ZIP_CODE", ""),
                    department=row.get("DEPT_CODE", ""),
                    co_ownership_charges=charges,
                )
                real_estate_ads_to_create.append(real_estate_ad)

        if real_estate_ads_to_create:
            RealEstateAd.objects.bulk_create(
                real_estate_ads_to_create, batch_size=10000, ignore_conflicts=True
            )

        self.stdout.write(self.style.SUCCESS("\nImport completed"))
