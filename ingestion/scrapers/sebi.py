import time
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base import BaseScraper, Document


class SEBIScraper(BaseScraper):
    """
    Scrapes regulatory documents from the Securities and Exchange Board of India (SEBI).
    Source: https://www.sebi.gov.in

    SEBI organises documents by category via URL parameters:
      sid=1 (Legal), ssid=7 (Circulars), ssid=3 (Regulations), ssid=6 (Master Circulars)
    """

    LISTING_URL = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do"
    BASE_SITE = "https://www.sebi.gov.in"

    # Map friendly names to SEBI's internal ssid values
    CATEGORY_SSID = {
        "circulars": 7,
        "regulations": 3,
        "master_circulars": 6,
        "guidelines": 5,
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; RegulatorIQ-ResearchBot/1.0; "
            "portfolio research project)"
        )
    }

    def __init__(self, category: str = "circulars"):
        if category not in self.CATEGORY_SSID:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Choose from: {list(self.CATEGORY_SSID)}"
            )
        self.category = category
        self.ssid = self.CATEGORY_SSID[category]

    def get_source_name(self) -> str:
        return f"SEBI {self.category.replace('_', ' ').title()}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def fetch_documents(self, count: int = 10) -> list[Document]:
        params = {
            "doListingAll": "yes",
            "sid": 1,
            "ssid": self.ssid,
            "smid": 0,
        }

        logger.info(f"Fetching SEBI {self.category} listing (up to {count} docs)")
        response = requests.get(
            self.LISTING_URL, params=params, headers=self.HEADERS, timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            logger.warning("No document table found on SEBI listing page")
            return []

        rows = table.find_all("tr")[1:]  # skip header row
        documents = []

        for row in rows[:count]:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            date_text = cells[0].get_text(strip=True)
            type_text = cells[1].get_text(strip=True)
            title_cell = cells[2]

            link = title_cell.find("a")
            if not link:
                continue

            title = link.get_text(strip=True)
            href = link.get("href", "")
            url = href if href.startswith("http") else self.BASE_SITE + href

            # Stable ID: last path segment before .html, prefixed with sebi-
            slug = url.rstrip("/").split("/")[-1].replace(".html", "")
            doc_id = f"sebi-{slug}"

            # Fetch the full text from the detail page (rate-limited)
            content = self._fetch_detail_content(url) or title
            time.sleep(0.5)  # be polite to the server

            doc = Document(
                id=doc_id,
                title=title,
                source=self.get_source_name(),
                content=content,
                published_date=date_text,
                url=url,
                metadata={
                    "type": type_text,
                    "regulator": "SEBI",
                    "category": self.category,
                },
            )
            documents.append(doc)

        logger.info(f"Fetched {len(documents)} documents from {self.get_source_name()}")
        return documents

    def _fetch_detail_content(self, url: str) -> str | None:
        """
        Fetches the full text from an individual SEBI document page.
        Returns None on failure so the caller can fall back to the title.
        """
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # SEBI detail pages put the main content in a div with class 'inner-page-content'
            # or inside the main article area — try common selectors in order
            for selector in [
                "div.inner-page-content",
                "div#wrapper",
                "div.content-area",
                "main",
                "article",
            ]:
                container = soup.select_one(selector)
                if container:
                    text = container.get_text(separator=" ", strip=True)
                    if len(text) > 100:
                        return text[:8000]  # cap at 8 KB to keep things manageable

            # Fallback: grab all paragraph text
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            return text[:8000] if len(text) > 100 else None

        except Exception as e:
            logger.warning(f"Could not fetch detail page {url}: {e}")
            return None
