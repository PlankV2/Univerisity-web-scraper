# University Cost Data Scraper

> **AI-powered Python tool** that scrapes tuition, housing, and cost-of-attendance data from university websites and exports clean, uniform CSV and JSON files.

---

## Features

- Scrapes multiple URLs per university (e.g. separate tuition and housing pages)
- Uses **Claude AI** to intelligently extract and categorize cost fields — no fragile regex
- Handles pagination, retries, and polite rate-limiting automatically
- Exports timestamped **CSV** and **JSON** files with uniform columns
- Fully configurable: add universities and cost fields in one file (`config.py`)
- Production-grade error handling and structured logging

---

## Project Structure

```
university_scraper/
├── main.py            ← Entry point; runs the full pipeline
├── config.py          ← Universities list, cost fields, and all settings
├── scraper.py         ← HTTP fetching + HTML-to-text extraction
├── extractor.py       ← Claude AI cost field extraction
├── exporter.py        ← CSV and JSON file writer
├── utils.py           ← Logging setup and console output helpers
├── requirements.txt   ← Python dependencies
└── output/            ← Generated output files (created automatically)
```

---

## Setup

### 1. Prerequisites

- Python 3.9 or higher
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

**macOS / Linux:**
```bash
export GEMINI_API_KEY="your-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-key-here"
```

> **Tip:** Add the export line to your `~/.bashrc` or `~/.zshrc` so you don't have to repeat it.

---

## Usage

### Run with defaults (outputs both CSV and JSON)
```bash
python main.py
```

### CSV only
```bash
python main.py --format csv
```

### JSON only
```bash
python main.py --format json
```

### Custom output directory
```bash
python main.py --output results/
```

### Verbose logging (debug mode)
```bash
python main.py --verbose
```

---

## Configuration

All configuration lives in **`config.py`**. No other file needs to be changed for typical usage.

### Adding universities

```python
UNIVERSITIES = [
    {
        "name": "Yale University",
        "urls": {
            "tuition": "https://your-tuition-page-url",
            "housing":  "https://your-housing-page-url",   # optional
        },
    },
    # ... more universities
]
```

### Adding cost fields

```python
COST_FIELDS = [
    "tuition_domestic",
    "tuition_international",
    "housing_on_campus",
    # Add any new field here — the AI will look for it automatically
    "student_union_fee",
]
```

---

## Output Format

Files are saved to `output/` with a timestamp in the filename:

```
output/
├── university_costs_20240601_143022.csv
└── university_costs_20240601_143022.json
```

### CSV example

| university_name | tuition_domestic | tuition_international | housing_on_campus | total_cost_of_attendance | currency | academic_year |
|---|---|---|---|---|---|---|
| MIT | $57,986 | $57,986 | $11,000–$17,000 | $85,960 | USD | 2024–2025 |
| Oxford | £9,250 | £26,770–£37,510 | £6,500–£9,000 | — | GBP | 2024–2025 |

### JSON example

```json
[
  {
    "university_name": "MIT",
    "tuition_domestic": "$57,986",
    "tuition_international": "$57,986",
    "housing_on_campus": "$11,000–$17,000",
    "total_cost_of_attendance": "$85,960",
    "currency": "USD",
    "academic_year": "2024–2025",
    "source_url": "tuition, housing"
  }
]
```

---

## How It Works

```
┌────────────┐    HTTP GET     ┌──────────────┐   Plain text   ┌─────────────┐
│ config.py  │ ─────────────► │  scraper.py  │ ─────────────► │ extractor.py│
│  (URL list)│                 │ (fetch+parse)│                 │ (Claude AI) │
└────────────┘                 └──────────────┘                 └──────┬──────┘
                                                                        │ JSON
                                                                        ▼
                                                               ┌─────────────────┐
                                                               │   exporter.py   │
                                                               │  CSV  •  JSON   │
                                                               └─────────────────┘
```

1. **`scraper.py`** fetches each URL using `requests`, then strips navigation, scripts, and clutter using `BeautifulSoup`, leaving only page content.
2. **`extractor.py`** sends the clean text to the Claude API with a structured prompt asking it to return a JSON object of cost fields.
3. **`exporter.py`** collects all records and writes them to uniform CSV and JSON files.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `google.auth.exceptions.DefaultCredentialsError` | Check that `GEMINI_API_KEY` is set correctly |
| `Connection error` | Check your internet connection; the university site may be blocking scrapers |
| Field shows `null` | The data wasn't found on the page — try adding another URL for that university in `config.py` |
| Rate limit warning | Increase `REQUEST_DELAY` in `config.py` |

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Built with Python 3, BeautifulSoup4, and Anthropic Claude.
