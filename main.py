"""
University Cost Data Scraper
=============================
Entry point. Orchestrates scraping → extraction → export pipeline.

Usage:
    python main.py
    python main.py --output results       # custom output folder
    python main.py --format csv           # csv only
    python main.py --format json          # json only
"""

import argparse
import logging
import sys
from pathlib import Path

from config import UNIVERSITIES, OUTPUT_DIR, LOG_LEVEL
from scraper import WebScraper
from extractor import CostExtractor
from exporter import DataExporter
from utils import setup_logging, print_banner, print_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape university tuition and cost data into structured CSV/JSON."
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        help="Directory to write output files (default: output/)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="both",
        help="Export format (default: both)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log_level = "DEBUG" if args.verbose else LOG_LEVEL
    logger = setup_logging(log_level)

    print_banner()

    scraper = WebScraper()
    extractor = CostExtractor()
    exporter = DataExporter(output_dir=args.output)

    results = []
    failed = []

    logger.info(f"Starting pipeline for {len(UNIVERSITIES)} universities...")

    for university in UNIVERSITIES:
        name = university["name"]
        urls = university["urls"]

        logger.info(f"\n{'─' * 50}")
        logger.info(f"Processing: {name}")

        # ── Step 1: Scrape raw page text from all configured URLs ──
        raw_pages = {}
        for label, url in urls.items():
            logger.info(f"  Scraping [{label}]: {url}")
            html, error = scraper.fetch(url)
            if error:
                logger.warning(f"  ✗ Failed to fetch {url}: {error}")
                continue
            text = scraper.extract_text(html)
            raw_pages[label] = text
            logger.info(f"  ✓ Fetched {len(text):,} characters")

        if not raw_pages:
            logger.error(f"  ✗ No pages could be fetched for {name}. Skipping.")
            failed.append(name)
            continue

        # ── Step 2: Use AI to extract and categorize cost fields ──
        logger.info(f"  Extracting structured data with AI...")
        data, error = extractor.extract(name, raw_pages)
        if error:
            logger.error(f"  ✗ Extraction failed: {error}")
            failed.append(name)
            continue

        results.append(data)
        logger.info(f"  ✓ Extracted {len([v for v in data.values() if v])} fields")

    # ── Step 3: Export to CSV and/or JSON ──
    logger.info(f"\n{'─' * 50}")
    if not results:
        logger.error("No results to export. Exiting.")
        sys.exit(1)

    export_fmt = args.format
    if export_fmt in ("csv", "both"):
        csv_path = exporter.to_csv(results)
        logger.info(f"✓ CSV saved: {csv_path}")

    if export_fmt in ("json", "both"):
        json_path = exporter.to_json(results)
        logger.info(f"✓ JSON saved: {json_path}")

    print_summary(results, failed)


if __name__ == "__main__":
    main()
