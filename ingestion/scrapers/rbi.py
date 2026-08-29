import time
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base import BaseScraper, Document


class RBIScraper(BaseScraper):
    """
    Scrapes regulatory circulars from the Reserve Bank of India (RBI).
    Source: https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx

    The listing page shows: Circular Number | Date | Department | Subject | Meant For
    Each row links to a detail page at ?Id=NNNNN with the full circular text.
    """

    LISTING_URL = "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx"
    BASE_SITE = "https://www.rbi.org.in"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; RegulatorIQ-ResearchBot/1.0; "
            "portfolio research project)"
        )
    }

    def get_source_name(self) -> str:
        return "RBI Circulars"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def fetch_documents(self, count: int = 10) -> list[Document]:
        logger.info(f"Fetching RBI circulars listing (up to {count} docs)")
        response = requests.get(
            self.LISTING_URL, headers=self.HEADERS, timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            logger.warning("No document table found on RBI circulars page")
            return []

        rows = table.find_all("tr")[1:]  # skip header row
        documents = []

        for row in rows[:count]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            # Cell 0: circular number + link (e.g. "RBI/2026-2027/248")
            # The hyperlink is on the circular number, NOT on the subject text.
            num_cell = cells[0]
            link = num_cell.find("a")
            if not link:
                continue

            circular_number = num_cell.get_text(separator="\n", strip=True).split("\n")[0].strip()
            href = link.get("href", "")
            # href is relative: "BS_CircularIndexDisplay.aspx?Id=13690"
            url = href if href.startswith("http") else "https://www.rbi.org.in/Scripts/" + href.lstrip("/")

            # Cell 1: date in dd.mm.yyyy format
            date_text = cells[1].get_text(strip=True)

            # Cell 2: department
            department = cells[2].get_text(strip=True)

            # Cell 3: subject / title (plain text, no link)
            title = cells[3].get_text(strip=True)

            # Stable ID from the numeric Id parameter in the URL
            doc_id_num = url.split("Id=")[-1] if "Id=" in url else circular_number
            doc_id = f"rbi-{doc_id_num}"

            # Meant For (cell 4 if present)
            meant_for = cells[4].get_text(strip=True) if len(cells) > 4 else ""

            # Fetch full text from the detail page
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
                    "circular_number": circular_number,
                    "department": department,
                    "meant_for": meant_for,
                    "regulator": "RBI",
                },
            )
            documents.append(doc)

        logger.info(f"Fetched {len(documents)} documents from {self.get_source_name()}")
        return documents

    def _fetch_detail_content(self, url: str) -> str | None:
        """
        Fetches the full circular text from an individual RBI detail page.
        Returns None on failure so the caller can fall back to the title.
        """
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # RBI detail pages use a main content wrapper — try common selectors
            for selector in [
                "div.contentarea",
                "div#wrapper",
                "div.content",
                "td.contentarea",
                "main",
            ]:
                container = soup.select_one(selector)
                if container:
                    text = container.get_text(separator=" ", strip=True)
                    if len(text) > 100:
                        return text[:8000]

            # Fallback: all paragraphs
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            return text[:8000] if len(text) > 100 else None

        except Exception as e:
            logger.warning(f"Could not fetch detail page {url}: {e}")
            return None
