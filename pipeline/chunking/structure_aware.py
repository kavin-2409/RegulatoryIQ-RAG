from dataclasses import dataclass
from loguru import logger


@dataclass
class Chunk:
    """One piece of a document, small enough to embed and search."""
    id: str           # e.g. "sebi-103915-chunk-0"
    doc_id: str       # parent document id
    text: str         # the actual text content
    chunk_index: int  # position within the document (0, 1, 2...)
    metadata: dict    # carries everything from the parent document


class StructureAwareChunker:
    """
    Splits regulatory documents into overlapping chunks.

    Strategy:
      1. Split at paragraph boundaries (double newlines) — respects document structure
      2. If a paragraph is still too long, split at sentence boundaries (. ! ?)
      3. Merge short paragraphs together until we reach the target size
      4. Add overlap so context is not lost at chunk boundaries

    Why overlap? If a regulation spans two chunks, the answer to a question
    might be split between them. Overlap ensures both chunks carry enough
    context for the AI to give a correct answer.
    """

    def __init__(
        self,
        chunk_size: int = 1000,   # target characters per chunk (~250 tokens)
        overlap: int = 150,        # characters repeated between adjacent chunks
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, doc_id: str, text: str, metadata: dict) -> list[Chunk]:
        """Split one document's text into a list of Chunk objects."""
        if not text or not text.strip():
            return []

        raw_chunks = self._split_text(text)
        chunks = []

        for i, chunk_text in enumerate(raw_chunks):
            chunk = Chunk(
                id=f"{doc_id}-chunk-{i}",
                doc_id=doc_id,
                text=chunk_text,
                chunk_index=i,
                metadata={**metadata, "chunk_index": i, "total_chunks": len(raw_chunks)},
            )
            chunks.append(chunk)

        logger.debug(f"Split {doc_id} into {len(chunks)} chunks")
        return chunks

    def _split_text(self, text: str) -> list[str]:
        """Core splitting logic — returns a list of overlapping text strings."""
        # Step 1: split at paragraph boundaries
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Step 2: if any paragraph is too long, split at sentences
        pieces = []
        for para in paragraphs:
            if len(para) <= self.chunk_size:
                pieces.append(para)
            else:
                pieces.extend(self._split_at_sentences(para))

        # Step 3: merge short pieces into chunks of target size
        chunks = []
        current = ""

        for piece in pieces:
            if not current:
                current = piece
            elif len(current) + len(piece) + 1 <= self.chunk_size:
                current += "\n\n" + piece
            else:
                chunks.append(current)
                # overlap: carry the tail of the previous chunk into the next
                overlap_text = current[-self.overlap:] if len(current) > self.overlap else current
                current = overlap_text + "\n\n" + piece

        if current:
            chunks.append(current)

        return chunks

    def _split_at_sentences(self, text: str) -> list[str]:
        """Splits a long paragraph at sentence endings (. ! ?)."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)

        pieces = []
        current = ""
        for sentence in sentences:
            if not current:
                current = sentence
            elif len(current) + len(sentence) + 1 <= self.chunk_size:
                current += " " + sentence
            else:
                pieces.append(current)
                current = sentence

        if current:
            pieces.append(current)

        return pieces
