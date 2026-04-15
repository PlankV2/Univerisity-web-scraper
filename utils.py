"""
utils.py — Shared helper functions (logging setup, console output).
===================================================================
Kept separate so main.py stays clean and readable.
"""

import logging
import sys
from typing import Dict, List


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure the root logger to print coloured, timestamped messages
    to stdout. Returns the root logger.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


def print_banner() -> None:
    banner = r"""
╔══════════════════════════════════════════════════════╗
║       University Cost Data Scraper  v1.0             ║
║       AI-Powered  •  CSV & JSON Export               ║
╚══════════════════════════════════════════════════════╝
"""
    print(banner)


def print_summary(results: List[Dict], failed: List[str]) -> None:
    print("\n" + "═" * 54)
    print("  SUMMARY")
    print("═" * 54)
    print(f"  ✓ Successfully processed : {len(results)}")
    print(f"  ✗ Failed                 : {len(failed)}")

    if failed:
        print("\n  Failed universities:")
        for name in failed:
            print(f"    • {name}")

    if results:
        print("\n  Extracted universities:")
        for rec in results:
            name = rec.get("university_name", "Unknown")
            coa  = rec.get("total_cost_of_attendance") or "—"
            curr = rec.get("currency") or ""
            print(f"    ✓ {name:<45}  CoA: {coa}")

    print("═" * 54 + "\n")
