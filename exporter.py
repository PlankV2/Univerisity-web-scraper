"""
exporter.py — Writes structured results to CSV and/or JSON files.
=================================================================
Handles output directory creation, timestamped filenames, and
column ordering to produce clean, analysis-ready files.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from config import COST_FIELDS

logger = logging.getLogger(__name__)

# Column order in the final CSV / JSON output
COLUMN_ORDER = ["university_name"] + COST_FIELDS


class DataExporter:
    """
    Exports a list of extracted university cost records to disk.
    """

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────────────

    def to_csv(self, records: List[Dict]) -> Path:
        """
        Write records to a timestamped CSV file.
        Returns the path to the created file.
        """
        filepath = self._timestamped_path("university_costs", "csv")
        ordered = self._order_columns(records)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_ORDER, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(ordered)

        logger.debug(f"CSV rows written: {len(ordered)}")
        return filepath

    def to_json(self, records: List[Dict]) -> Path:
        """
        Write records to a timestamped JSON file (pretty-printed).
        Returns the path to the created file.
        """
        filepath = self._timestamped_path("university_costs", "json")
        ordered = self._order_columns(records)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(ordered, f, indent=2, ensure_ascii=False)

        logger.debug(f"JSON records written: {len(ordered)}")
        return filepath

    # ──────────────────────────────────────────────────────
    #  PRIVATE HELPERS
    # ──────────────────────────────────────────────────────

    def _timestamped_path(self, stem: str, extension: str) -> Path:
        """Generate output/university_costs_20240601_143022.csv"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{stem}_{ts}.{extension}"

    def _order_columns(self, records: List[Dict]) -> List[Dict]:
        """
        Return records with keys in COLUMN_ORDER.
        Missing fields are filled with None so every row is uniform.
        """
        return [
            {col: record.get(col) for col in COLUMN_ORDER}
            for record in records
        ]
