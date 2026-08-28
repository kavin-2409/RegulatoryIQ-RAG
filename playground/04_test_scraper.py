import sys
sys.path.insert(0, ".")  # makes sure Python can find the ingestion/ folder

from ingestion.scrapers.federal_register import FederalRegisterScraper

scraper = FederalRegisterScraper()

print("Source name:", scraper.get_source_name())
print()

docs = scraper.fetch_documents(count=3)

for doc in docs:
    print(f"ID:      {doc.id}")
    print(f"Title:   {doc.title}")
    print(f"Source:  {doc.source}")
    print(f"Date:    {doc.published_date}")
    print(f"URL:     {doc.url}")
    print(f"Agencies:{doc.metadata['agencies']}")
    print()
