"""
extractor.py — Uses the Google Gemini API to intelligently extract cost fields.
================================================================================
Rather than fragile regex patterns, we pass the scraped text to an LLM and
ask it to return a structured JSON object. This is robust against layout
changes on university websites.
"""

import json
import logging
from typing import Dict, Optional, Tuple

from google import genai
from google.genai import types

from config import COST_FIELDS, AI_MODEL, AI_MAX_TOKENS, AI_TEXT_LIMIT, GEMINI_API_KEY

logger = logging.getLogger(__name__)


class CostExtractor:
    """
    Uses the Google Gemini API to extract cost data from raw page text.

    Why AI instead of regex?
    ─────────────────────────
    University websites present the same data in wildly different formats:
    - Tables with merged cells
    - Bullet lists
    - Inline paragraphs ("Tuition for the 2024–25 year is $58,590")
    - Different labels ("Cost of Attendance", "Tuition & Fees", "Annual Charges")

    An LLM understands all of these naturally, making the extractor resilient
    to site redesigns without any code changes.
    """

    def __init__(self) -> None:
        # New unified Google GenAI SDK (replaces deprecated google-generativeai)
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    # ──────────────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────────────

    def extract(
        self,
        university_name: str,
        raw_pages: Dict[str, str],
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Given a university name and a dict of { page_label: page_text },
        return (structured_data_dict, error_message).

        On success: (dict, None)
        On failure: (None, error)
        """
        combined_text = self._combine_pages(raw_pages)
        prompt = self._build_prompt(university_name, combined_text)

        try:
            response = self.client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self._system_prompt(),
                    max_output_tokens=AI_MAX_TOKENS,
                    # Force JSON output — no markdown fences, no prose
                    response_mime_type="application/json",
                ),
            )

            raw_response = response.text
            data = self._parse_json(raw_response)

            if data is None:
                return None, "AI returned invalid JSON"

            # Always stamp the university name and source URLs
            data["university_name"] = university_name
            data["source_url"] = ", ".join(raw_pages.keys())

            return data, None

        except Exception as e:
            return None, f"Gemini API error: {e}"

    # ──────────────────────────────────────────────────────
    #  PRIVATE HELPERS
    # ──────────────────────────────────────────────────────

    def _combine_pages(self, raw_pages: Dict[str, str]) -> str:
        """Merge all scraped page texts with section labels."""
        parts = []
        for label, text in raw_pages.items():
            # Truncate each page so we stay within the AI context limit
            truncated = text[: AI_TEXT_LIMIT // len(raw_pages)]
            parts.append(f"=== PAGE: {label.upper()} ===\n{truncated}")
        return "\n\n".join(parts)

    def _system_prompt(self) -> str:
        return (
            "You are a precise data extraction assistant. "
            "Your only job is to extract cost and tuition data from university website text "
            "and return it as valid JSON. "
            "Never add commentary, explanations, or markdown fences. "
            "Return ONLY the raw JSON object and nothing else."
        )

    def _build_prompt(self, university_name: str, page_text: str) -> str:
        fields_description = "\n".join(
            f'  "{field}": <value or null if not found>'
            for field in COST_FIELDS
        )

        return f"""
Extract cost and tuition data for "{university_name}" from the university website text below.

Return a single JSON object with EXACTLY these fields:
{{
{fields_description}
}}

Rules:
- Use null for any field not found in the text.
- Include the currency symbol in monetary values (e.g. "$58,590/year" or "£9,250").
- For ranges, use a string like "$15,000 – $20,000".
- "academic_year" should be formatted like "2024–2025".
- Keep notes concise (max 1 sentence).
- Do NOT invent or estimate values. Only extract what is explicitly stated.

Website text:
─────────────────────────────────────────
{page_text}
─────────────────────────────────────────

Return ONLY the JSON object. No explanation. No markdown.
"""

    def _parse_json(self, raw: str) -> Optional[Dict]:
        """
        Safely parse the AI's response as JSON.
        Strips accidental markdown fences if the model added them.
        """
        cleaned = raw.strip()

        # Strip ```json ... ``` fences if present (defensive)
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw response:\n{raw[:500]}")
            return None
