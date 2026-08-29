import sys
sys.path.insert(0, ".")

from pipeline.chunking.structure_aware import StructureAwareChunker

# Sample regulatory text (simulates a real SEBI circular)
sample_text = """
Securities and Exchange Board of India

Circular No. SEBI/HO/MRD/2026/103915
Date: August 24, 2026

Subject: Alignment of SEBI's Cyber Incident Reporting Portal with FIRE Format

1. Background

The Financial Industry Regulatory Entity (FIRE) format has been established as
a standardized framework for reporting cybersecurity incidents across financial
institutions. SEBI has decided to align its Cyber Incident Reporting Portal
with the FIRE format to ensure consistency and interoperability.

2. Applicability

This circular is applicable to all Market Infrastructure Institutions (MIIs),
including Stock Exchanges, Clearing Corporations, and Depositories registered
with SEBI.

3. Requirements

All regulated entities shall report cyber incidents using the FIRE format
within 6 hours of detection of any significant cyber incident. The report
must include: nature of the incident, systems affected, data compromised,
remediation steps taken, and estimated recovery timeline.

4. Timeline

The provisions of this circular shall come into effect from October 1, 2026.
All entities must complete the integration with the updated portal by
September 30, 2026.

5. Non-Compliance

Failure to comply with these provisions may attract penal action under the
relevant provisions of SEBI Act, 1992.
"""

print("=" * 50)
print("Testing Structure-Aware Chunker")
print("=" * 50)

chunker = StructureAwareChunker(chunk_size=500, overlap=100)
chunks = chunker.chunk(
    doc_id="sebi-103915",
    text=sample_text,
    metadata={"source": "SEBI Circulars", "regulator": "SEBI"},
)

print(f"\nTotal chunks created: {len(chunks)}\n")

for chunk in chunks:
    print(f"--- Chunk {chunk.chunk_index} (ID: {chunk.id}) ---")
    print(f"Length: {len(chunk.text)} characters")
    print(f"Text preview: {chunk.text[:200]}")
    print()

print("Notice: adjacent chunks share some overlapping text.")
print("This ensures questions spanning chunk boundaries are still answered correctly.")
