import sys
sys.path.insert(0, ".")

from ingestion.scrapers.sebi import SEBIScraper
from ingestion.scrapers.rbi import RBIScraper
from ingestion.versioning.hasher import hash_document, has_changed
from ingestion.versioning.store import VersionStore

# --- Step 1: Scrape documents from both Indian regulators ---
print("=" * 50)
print("STEP 1: Scraping documents")
print("=" * 50)

all_docs = []

sebi = SEBIScraper(category="circulars")
sebi_docs = sebi.fetch_documents(count=3)
print(f"SEBI: fetched {len(sebi_docs)} documents")
all_docs.extend(sebi_docs)

rbi = RBIScraper()
rbi_docs = rbi.fetch_documents(count=3)
print(f"RBI:  fetched {len(rbi_docs)} documents")
all_docs.extend(rbi_docs)

print(f"\nTotal: {len(all_docs)} documents\n")

# --- Step 2: Set up the version store ---
print("=" * 50)
print("STEP 2: Setting up version store")
print("=" * 50)
store = VersionStore()
print()

# --- Step 3: Hash each document and check if it changed ---
print("=" * 50)
print("STEP 3: Checking for new/changed documents")
print("=" * 50)

new_count = 0
for doc in all_docs:
    doc_hash = hash_document(doc.content)
    changed = has_changed(doc.id, doc_hash, store)

    if changed:
        store.save_version(doc.id, doc_hash, doc.content, doc.metadata)
        print(f"  NEW:       {doc.title[:65]}")
        new_count += 1
    else:
        print(f"  UNCHANGED: {doc.title[:65]}")

print(f"\nSaved {new_count} new documents\n")

# --- Step 4: Show all tracked documents ---
print("=" * 50)
print("STEP 4: All tracked documents in database")
print("=" * 50)
all_tracked = store.get_all_documents()
for d in all_tracked:
    print(f"  {d['doc_id']}  (v{d['latest_version']})  {d['last_seen']}")

print("\nRun this script a second time — all documents will show UNCHANGED.")
