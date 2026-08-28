# ── CONCEPT 1: Variables ──────────────────────────────────────────
name = "RegulatorIQ"
version = 1
is_ready = False

print(name)      # RegulatorIQ
print(version)   # 1
print(is_ready)  # False

# ── CONCEPT 2: Lists (ordered collection) ─────────────────────────
sources = ["SEC EDGAR", "Federal Register", "FDA"]

print(sources[0])        # SEC EDGAR  (index starts at 0)
print(sources[-1])       # FDA        (last item)
print(len(sources))      # 3

for source in sources:
    print("Source:", source)

# ── CONCEPT 3: Dictionaries (key → value pairs) ───────────────────
# This is what every API response looks like
document = {
    "title": "SEC Data Retention Rule 2024",
    "agency": "SEC",
    "date": "2024-10-15",
    "word_count": 4200
}

print(document["title"])    # SEC Data Retention Rule 2024
print(document["agency"])   # SEC

# Add a new key
document["status"] = "new"
print(document)

# ── CONCEPT 4: Functions ──────────────────────────────────────────
def greet_document(doc):
    return f"Processing: {doc['title']} from {doc['agency']}"

result = greet_document(document)
print(result)
