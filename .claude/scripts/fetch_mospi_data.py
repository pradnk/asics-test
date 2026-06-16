#!/usr/bin/env python3
"""
Fetch environmental statistics from MOSPI API.
Iterates indicator_code 1–130, stops on empty/error response.
Saves each result as a JSON file named after the indicator field.
"""

import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Union

BASE_URL = "https://api.mospi.gov.in/api/env/getEnvStatsRecords"
OUTPUT_DIR =  Path("../../data") / "mospi"
MAX_INDICATOR = 130
DELAY_SECONDS = 1  # polite delay between requests

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (research/data-fetch)",
}


def sanitize_filename(name: str) -> str:
    """Convert an indicator name to a safe filename."""
    name = name.strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', "_", name)
    return name or "unknown"


def fetch_indicator(code: int) -> Optional[Union[dict, list]]:
    """Fetch one indicator. Returns parsed JSON, or None on error/empty."""
    url = f"{BASE_URL}?indicator_code={code}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            # Treat empty list/dict/null as "no data"
            if not data:
                return None
            return data
    except urllib.error.HTTPError as e:
        print(f"  HTTP error for code {code}: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"  URL error for code {code}: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"  JSON decode error for code {code}: {e}")
        return None


def extract_indicator_name(data: Union[dict, list], code: int) -> str:
    """Pull the indicator name out of the response, falling back to the code."""
    record = data[0] if isinstance(data, list) and data else data
    if isinstance(record, dict):
        for key in ("indicator", "indicator_name", "Indicator", "IndicatorName"):
            if key in record and record[key]:
                return sanitize_filename(str(record[key]))
    return f"indicator_{code}"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}\n")

    saved = 0
    for code in range(1, MAX_INDICATOR + 1):
        print(f"Fetching indicator_code={code} ...", end=" ", flush=True)
        data = fetch_indicator(code)

        if data is None:
            print("empty / error — stopping.")
            break

        name = extract_indicator_name(data, code)
        filename = OUTPUT_DIR / f"{name}.json"

        # If a file with that name already exists, append the code to avoid collision
        if filename.exists():
            filename = OUTPUT_DIR / f"{name}_{code}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"saved → {filename.name}")
        saved += 1
        time.sleep(DELAY_SECONDS)

    print(f"\nDone. {saved} file(s) written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
