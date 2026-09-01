"""
Curated evaluation dataset for RegulatorIQ.
Each entry has a question and key reference terms that a correct answer must cover.
Using reference_terms (not exact sentences) so local metrics are meaningful
without needing a ground-truth LLM judge.
"""

EVAL_DATASET = [
    {
        "id": "sebi_01",
        "source": "SEBI",
        "question": "What are the SEBI cybersecurity requirements for stock brokers?",
        "reference_terms": ["cybersecurity", "broker", "incident", "reporting", "SEBI"],
    },
    {
        "id": "sebi_02",
        "source": "SEBI",
        "question": "What is the IT Resilience Index for Market Infrastructure Institutions?",
        "reference_terms": ["IT resilience", "market infrastructure", "index", "MII"],
    },
    {
        "id": "sebi_03",
        "source": "SEBI",
        "question": "What are SEBI's regulations on algorithmic trading?",
        "reference_terms": ["algorithmic", "algo", "trading", "SEBI", "exchange"],
    },
    {
        "id": "sebi_04",
        "source": "SEBI",
        "question": "What are the SEBI guidelines for mutual fund investments?",
        "reference_terms": ["mutual fund", "scheme", "investment", "SEBI"],
    },
    {
        "id": "sebi_05",
        "source": "SEBI",
        "question": "What are the disclosure requirements for listed companies under SEBI?",
        "reference_terms": ["disclosure", "listed", "company", "SEBI", "material"],
    },
    {
        "id": "rbi_01",
        "source": "RBI",
        "question": "What is the Cash Reserve Ratio requirement set by RBI for commercial banks?",
        "reference_terms": ["Cash Reserve Ratio", "CRR", "bank", "RBI", "reserve"],
    },
    {
        "id": "rbi_02",
        "source": "RBI",
        "question": "What are RBI guidelines on Know Your Customer norms?",
        "reference_terms": ["KYC", "Know Your Customer", "customer", "identity", "RBI"],
    },
    {
        "id": "rbi_03",
        "source": "RBI",
        "question": "What are RBI directions on priority sector lending?",
        "reference_terms": ["priority sector", "lending", "bank", "RBI", "target"],
    },
    {
        "id": "rbi_04",
        "source": "RBI",
        "question": "What is the Statutory Liquidity Ratio mandated by RBI?",
        "reference_terms": ["Statutory Liquidity Ratio", "SLR", "liquid assets", "bank", "RBI"],
    },
    {
        "id": "rbi_05",
        "source": "RBI",
        "question": "What are RBI's regulations on Non-Banking Financial Companies?",
        "reference_terms": ["NBFC", "Non-Banking Financial", "RBI", "registration", "regulation"],
    },
]
