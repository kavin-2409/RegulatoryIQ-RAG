import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base import BaseScraper, Document


class FederalRegisterScraper(BaseScraper):
    """Downloads regulatory documents from federalregister.gov (free, no auth required)."""

    BASE_URL = "https://www.federalregister.gov/api/v1/documents"
    FIELDS = ["title", "agency_names", "publication_date", "abstract",
              "full_text_xml_url", "html_url", "document_number", "type"]

    def get_source_name(self) -> str:
        return "Federal Register"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def fetch_documents(self, count: int = 10) -> list[Document]:
        """
        Fetch the most recent documents from the Federal Register API.
        Retries up to 3 times if the request fails.
        """
        logger.info(f"Fetching {count} documents from {self.get_source_name()}")

        params = {
            "per_page": count,
            "order": "newest",
            "fields[]": self.FIELDS,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=15)
        response.raise_for_status()  # raises an error if status code is not 200

        results = response.json().get("results", [])
        documents = []

        for item in results:
            doc = Document(
                id=f"fr-{item['document_number']}",
                title=item.get("title", "Untitled"),
                source=self.get_source_name(),
                content=item.get("abstract") or item.get("title", ""),
                published_date=item.get("publication_date", ""),
                url=item.get("html_url", ""),
                metadata={
                    "agencies": item.get("agency_names", []),
                    "type": item.get("type", ""),
                    "document_number": item.get("document_number", ""),
                    "full_text_xml_url": item.get("full_text_xml_url", ""),
                }
            )
            documents.append(doc)

        logger.success(f"Fetched {len(documents)} documents from {self.get_source_name()}")
        return documents
