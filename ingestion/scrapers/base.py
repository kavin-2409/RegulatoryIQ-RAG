from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Document:
    """Represents one regulatory document downloaded from any source."""
    id: str                    # unique identifier (e.g. "fr-2024-12345")
    title: str                 # document title
    source: str                # which API it came from ("Federal Register", "SEC EDGAR")
    content: str               # full text of the document
    published_date: str        # "2024-10-15"
    url: str                   # link to the original document
    metadata: dict = field(default_factory=dict)  # any extra fields


class BaseScraper(ABC):
    """
    Abstract base class all scrapers must extend.
    Defines the interface the rest of the system expects.
    """

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this data source."""
        ...

    @abstractmethod
    def fetch_documents(self, count: int = 10) -> list[Document]:
        """Download and return a list of Documents."""
        ...
