import requests
import json
import os

# ── CONCEPT 1: Making an HTTP request ─────────────────────────────
# This calls the real Federal Register API - no API key needed
print("Calling Federal Register API...")

url = "https://www.federalregister.gov/api/v1/documents"
params = {
    "per_page": 3,          # only fetch 3 documents
    "order": "newest",      # most recent first
    "fields[]": ["title", "agency_names", "publication_date", "abstract"]
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)  # 200 means success
print()

# ── CONCEPT 2: Reading the JSON response ──────────────────────────
# The API sends back JSON - Python turns it into a dictionary automatically
data = response.json()

print("Total documents available:", data["count"])
print("Documents fetched:", len(data["results"]))
print()

# ── CONCEPT 3: Looping through results ────────────────────────────
for i, doc in enumerate(data["results"]):
    print(f"Document {i + 1}:")
    print(f"  Title:   {doc['title']}")
    print(f"  Agency:  {doc['agency_names']}")
    print(f"  Date:    {doc['publication_date']}")
    print()

# ── CONCEPT 4: Saving to a file ───────────────────────────────────
# Create a folder to store the downloaded data
os.makedirs("playground/data", exist_ok=True)

# Save the raw API response as a JSON file
with open("playground/data/sample_documents.json", "w") as f:
    json.dump(data["results"], f, indent=2)

print("Saved to playground/data/sample_documents.json")
