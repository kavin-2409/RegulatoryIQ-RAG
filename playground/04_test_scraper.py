import sys
sys.path.insert(0, ".")

from ingestion.scrapers.sebi import SEBIScraper
from ingestion.scrapers.rbi import RBIScraper

# --- Test SEBI ---
print("=" * 50)
print("Testing SEBI Circulars Scraper")
print("=" * 50)

sebi = SEBIScraper(category="circulars")
print("Source name:", sebi.get_source_name())
print()

sebi_docs = sebi.fetch_documents(count=3)
for doc in sebi_docs:
    print(f"ID:      {doc.id}")
    print(f"Title:   {doc.title}")
    print(f"Source:  {doc.source}")
    print(f"Date:    {doc.published_date}")
    print(f"URL:     {doc.url}")
    print(f"Content: {doc.content[:100]}...")
    print()

# --- Test RBI ---
print("=" * 50)
print("Testing RBI Circulars Scraper")
print("=" * 50)

rbi = RBIScraper()
print("Source name:", rbi.get_source_name())
print()

rbi_docs = rbi.fetch_documents(count=3)
for doc in rbi_docs:
    print(f"ID:         {doc.id}")
    print(f"Title:      {doc.title}")
    print(f"Source:     {doc.source}")
    print(f"Date:       {doc.published_date}")
    print(f"Circular#:  {doc.metadata['circular_number']}")
    print(f"Dept:       {doc.metadata['department']}")
    print(f"Content:    {doc.content[:100]}...")
    print()
