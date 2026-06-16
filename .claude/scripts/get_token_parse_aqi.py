#!/usr/bin/env python3

import json
import re
import time
import urllib.request
import urllib.parse

from pathlib import Path
from datetime import datetime

AQI_HOME = "https://www.aqi.in"
TOKEN_FILE = "aqi_tokens.json"
CITIES_FILE = "cities.md"

def fetch_homepage():

    request = urllib.request.Request(
        AQI_HOME,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def extract_tokens(html):

    patterns = [
        r'siteStore.*?"token":"(eyJ[^"]+)".*?"token2":"(eyJ[^"]+)"',
        r'siteStore.*?\\"token\\":\\"(eyJ[^"]+)\\".*?\\"token2\\":\\"(eyJ[^"]+)\\"',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.DOTALL
        )

        if match:
            return {
                "token": match.group(1),
                "token2": match.group(2),
            }

    raise Exception(
        "Could not locate token/token2 inside siteStore"
    )


def save_tokens(tokens):

    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"Saved tokens to {TOKEN_FILE}")


def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)

def fetch_city_data(city_slug, token2):

    params = urllib.parse.urlencode(
        {
            "slug": city_slug,
            "slugType": "cityId",
            "sensorname": "aqi",
            "source": "web",
        }
    )

    url = (
        "https://apiserver.aqi.in/aqi/v2/getAqiCalender?"
        + params
    )

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token2}",
            "Origin": "https://www.aqi.in",
            "Referer": "https://www.aqi.in/",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            ),
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )

def save_city_file(
    city_slug,
    payload,
    snapshot_date
    ):


    parts = city_slug.split("/")

    if len(parts) < 3:
        raise Exception(
            f"Malformed slug: {city_slug}"
        )

    output_dir = (
        Path("../../data")
        / Path("aqi")
        / Path(*parts[:-1])
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filepath = output_dir / f"{parts[-1]}.json"

    output = {
        "slug": city_slug,
        "country": parts[0],
        "state": parts[1],
        "city": parts[-1],
        "snapshot_date": snapshot_date,
        "fetched_at": int(time.time()),
        "data": payload,
    }

    with open(filepath, "w") as f:
        json.dump(
            output,
            f,
            indent=2
        )

    return filepath

def main():
    print("Fetching AQI homepage...")

html = fetch_homepage()

print("Extracting tokens...")

tokens = extract_tokens(html)

save_tokens(tokens)

print()
print("token:")
print(tokens["token"][:80] + "...")

print()
print("token2:")
print(tokens["token2"][:80] + "...")

with open(CITIES_FILE) as f:

    cities = [
        line.strip()
        for line in f.readlines()
        if line.strip()
        and not line.startswith("#")
    ]

print()
print(
    f"Found {len(cities)} cities"
)

snapshot_date = (
    datetime.utcnow()
    .strftime("%Y-%m-%d")
)

for city_slug in cities:

    try:

        payload = fetch_city_data(
            city_slug,
            tokens["token2"]
        )

        filepath = save_city_file(
            city_slug,
            payload,
            snapshot_date
        )

        print(f"✓ {filepath}")

        time.sleep(0.5)

    except Exception as e:

        print(
            f"✗ {city_slug}: {e}"
        )

if __name__ == "__main__":
    main()