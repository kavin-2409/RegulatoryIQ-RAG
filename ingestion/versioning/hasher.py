import hashlib


def hash_document(content: str) -> str:
    """
    Creates a unique fingerprint of a document's content.
    Same content always produces the same hash.
    Different content produces a different hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def has_changed(doc_id: str, new_hash: str, store) -> bool:
    """
    Returns True if the document content is different from
    the last time we saw it. Returns False if nothing changed.
    """
    previous_hash = store.get_latest_hash(doc_id)

    if previous_hash is None:
        return True  # never seen before — treat as new

    return previous_hash != new_hash
