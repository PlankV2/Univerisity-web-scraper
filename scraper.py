"""
scraper.py — Fetches web pages and extracts clean text content.
===============================================================
Handles HTTP requests, retries, rate limiting, and HTML → text conversion.
"""

import logging
import time
from typing import Optional, Tuple
import sys

import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES

logger = logging.getLogger(__name__)

# HTML tags that are purely structural and contain no useful cost data
_NOISE_TAGS = [
    "script", "style", "nav", "footer", "header",
    "noscript", "aside", "form", "button", "svg", "iframe",
]


class WebScraper:
    """
    Responsible for:
      1. Fetching a URL with retry logic.
      2. Stripping HTML down to readable plain text.
    """

    def __init__(self) -> None:
        # requests.Session reuses the TCP connection — faster for multiple pages
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    # ──────────────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────────────

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch a URL and return (html_string, error_message).
        On success: (html, None)
        On failure: (None, error)

        Retries up to MAX_RETRIES times with exponential back-off.
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                time.sleep(REQUEST_DELAY)   # be polite to servers
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status() # raises for 4xx / 5xx status codes
                return response.text, None

            except requests.exceptions.HTTPError as e:
                # E.g. 404 Not Found — retrying won't help
                return None, f"HTTP {e.response.status_code}: {url}"

            except requests.exceptions.ConnectionError:
                error = f"Connection error on attempt {attempt}/{MAX_RETRIES}: {url}"
                logger.warning(error)

            except requests.exceptions.Timeout:
                error = f"Timeout on attempt {attempt}/{MAX_RETRIES}: {url}"
                logger.warning(error)

            except requests.exceptions.RequestException as e:
                return None, f"Unexpected error: {e}"

            # Exponential back-off: 2s, 4s, 8s …
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                logger.info(f"  Retrying in {wait}s...")
                time.sleep(wait)

        return None, f"All {MAX_RETRIES} attempts failed: {url}"

    def extract_text(self, html: str) -> str:
        """
        Convert raw HTML into clean, readable plain text.

        Strategy:
          1. Parse HTML with BeautifulSoup.
          2. Remove noise tags (nav, script, style, etc.).
          3. Extract text from meaningful content areas first
             (tables, lists, headings, paragraphs) — these are most
             likely to contain cost data.
          4. Collapse excess whitespace.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove clutter
        for tag in soup(_NOISE_TAGS):
            tag.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        print(text, file=sys.stdout)

        # Collapse runs of whitespace / blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
