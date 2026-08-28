import requests
import json
import os

# ── What is a class? ──────────────────────────────────────────────
# A class is a blueprint for creating objects.
# Instead of writing the same functions over and over,
# you group related data + functions together in one place.
#
# Every file in RegulatorIQ is built this way.
# Example: FederalRegisterScraper is a class that knows
# how to download documents from one specific API.

class FederalRegisterScraper:

    def __init__(self):
        # __init__ runs automatically when you create the object.
        # Think of it as "setup".
        self.source_name = "Federal Register"
        self.base_url = "https://www.federalregister.gov/api/v1/documents"
        print(f"Scraper ready for: {self.source_name}")

    def fetch_documents(self, count=5):
        # A method = a function that belongs to the class.
        # self gives it access to base_url and source_name above.
        print(f"Fetching {count} documents...")

        params = {
            "per_page": count,
            "order": "newest",
            "fields[]": ["title", "agency_names", "publication_date", "abstract"]
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()
        return data["results"]

    def save(self, documents, filename):
        # Another method - saves documents to a JSON file.
        os.makedirs("playground/data", exist_ok=True)
        path = f"playground/data/{filename}"

        with open(path, "w") as f:
            json.dump(documents, f, indent=2)

        print(f"Saved {len(documents)} documents to {path}")

    def summarize(self, documents):
        # Loops through documents and prints a clean summary.
        print(f"\n── {self.source_name} Results ──")
        for i, doc in enumerate(documents):
            print(f"{i + 1}. {doc['title']}")
            print(f"   {doc['agency_names']} | {doc['publication_date']}")
        print()


# ── Using the class ───────────────────────────────────────────────
# Create an instance of the scraper (runs __init__)
scraper = FederalRegisterScraper()

# Call its methods
docs = scraper.fetch_documents(count=4)
scraper.summarize(docs)
scraper.save(docs, "federal_register_latest.json")

# ── Key insight ───────────────────────────────────────────────────
# In the real project, ingestion/scrapers/federal_register.py
# is exactly this class, but more polished.
# ingestion/scrapers/sec_edgar.py is another class just like it.
# Both extend base.py which defines what every scraper must have.
print("This is exactly what ingestion/scrapers/federal_register.py will look like.")
