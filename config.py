"""
config.py — Central configuration for the university cost scraper.
================================================================
Edit UNIVERSITIES to add/remove schools and their cost page URLs.
Edit COST_FIELDS to change what data categories are extracted.
"""

# ─────────────────────────────────────────────
#  OUTPUT SETTINGS
# ─────────────────────────────────────────────

OUTPUT_DIR = "output"           # Folder where CSV/JSON files will be saved
LOG_LEVEL  = "INFO"             # DEBUG | INFO | WARNING | ERROR


# ─────────────────────────────────────────────
#  UNIVERSITIES TO SCRAPE
#  Add as many as you like.
#  'urls' is a dict of { label: url } pairs.
#  Multiple URLs per university lets the AI
#  pull data from tuition pages AND housing pages.
# ─────────────────────────────────────────────

UNIVERSITIES = [
    {
        "name": "Massachusetts Institute of Technology",
        "urls": {
            "tuition": "https://sfs.mit.edu/undergraduate-students/the-cost-of-attendance/",
            "housing":  "https://studentlife.mit.edu/housing/costs",
        },
    },
    {
        "name": "Stanford University",
        "urls": {
            "tuition": "https://financialaid.stanford.edu/undergrad/how/budget.html",
        },
    },
    {
        "name": "Harvard University",
        "urls": {
            "tuition": "https://college.harvard.edu/financial-aid/apply/cost-attendance",
        },
    },
    {
        "name": "University of Oxford",
        "urls": {
            "tuition": "https://www.ox.ac.uk/admissions/undergraduate/fees-and-funding/tuition-fees",
            "housing":  "https://www.ox.ac.uk/students/life/accommodation/costs",
        },
    },
    {
        "name": "University of Cincinnati",
        "urls": {
            "tuition": "https://www.uc.edu/about/international/admissions/cost.html#undergrad",
        },
    },
]


# ─────────────────────────────────────────────
#  COST FIELDS TO EXTRACT
#  These are the categories the AI will look
#  for and populate. Add or remove fields here.
# ─────────────────────────────────────────────

COST_FIELDS = [
    "tuition_domestic",          # Tuition for domestic/local students (per year)
    "tuition_international",     # Tuition for international students (per year)
    "tuition_notes",             # Any important notes about tuition (e.g. fixed vs variable)
    "housing_on_campus",         # On-campus accommodation cost (per year)
    "housing_off_campus",        # Estimated off-campus rent (per year)
    "housing_notes",             # Notes about housing options
    "meal_plan",                 # Meal plan / food budget (per year)
    "books_supplies",            # Books and academic supplies (per year)
    "personal_expenses",         # Personal / miscellaneous expenses (per year)
    "health_insurance",          # Student health insurance (per year)
    "transportation",            # Transportation costs (per year)
    "total_cost_of_attendance",  # Full estimated Cost of Attendance (COA)
    "currency",                  # Currency (USD, GBP, EUR, etc.)
    "academic_year",             # Which academic year the figures apply to
    "source_url",                # URL the data was pulled from
]


# ─────────────────────────────────────────────
#  HTTP SETTINGS
# ─────────────────────────────────────────────

REQUEST_TIMEOUT = 20            # Seconds before a page fetch times out
REQUEST_DELAY   = 1.5           # Polite delay (seconds) between requests
MAX_RETRIES     = 3             # How many times to retry a failed request

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ─────────────────────────────────────────────
#  AI MODEL SETTINGS
# ─────────────────────────────────────────────

import os

# Your Gemini API key — set as an environment variable for security.
# Get one free at: https://aistudio.google.com/app/apikey
#
# Set it in your terminal before running:
#   macOS/Linux : export GEMINI_API_KEY="your-key-here"
#   Windows CMD : set GEMINI_API_KEY=your-key-here
#
# Never paste your key directly into this file if sharing code publicly.
GEMINI_API_KEY = "AIzaSyAAqkgR2b_sl007wKzzJw4eABDiMyNjF9I"

AI_MODEL      = "gemini-2.5-flash"   # Fast and cheap; swap to "gemini-2.5-pro" for higher accuracy
AI_MAX_TOKENS = 4000
# Max characters of scraped text sent to AI per university
# (keeps API costs low; most cost pages are short)
AI_TEXT_LIMIT = 24_000
