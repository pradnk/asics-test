#!/usr/bin/env python3
"""Push AQI JSON data to all Google Sheets tabs."""

import json
import statistics
from collections import defaultdict
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ"
SCRIPT_DIR = Path(__file__).parent
KEY_FILE = Path.home() / "keys" / "sheets-key.json"
DATA_DIR = SCRIPT_DIR / "data" / "aqi"
CITIES_FILE = SCRIPT_DIR / "cities.md"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MONTH_NAMES = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

AQI_CATEGORIES = [
    (50,  "Good"),
    (100, "Moderate"),
    (150, "Poor"),
    (200, "Unhealthy"),
    (300, "Severe"),
    (float("inf"), "Hazardous"),
]

def aqi_category(val):
    try:
        v = float(val)
    except (TypeError, ValueError):
        return ""
    for threshold, cat in AQI_CATEGORIES:
        if v <= threshold:
            return cat
    return "Hazardous"

def display_name(slug_part):
    """Convert slug segment to display name: new-delhi → New Delhi."""
    return " ".join(w.capitalize() for w in slug_part.split("-"))

def load_cities_order():
    with open(CITIES_FILE) as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]

def load_all_data():
    results = {}
    for p in DATA_DIR.rglob("*.json"):
        with open(p) as f:
            d = json.load(f)
        results[d["slug"]] = d
    return results

def clear_and_write(service, sheet_name, rows, existing_tabs):
    if sheet_name not in existing_tabs:
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={
            "requests": [{"addSheet": {"properties": {"title": sheet_name}}}]
        }).execute()
        print(f"  Created tab: {sheet_name}")

    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID, range=f"'{sheet_name}'!A:Z"
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()
    print(f"  '{sheet_name}': {len(rows)-1} data rows written")

def main():
    creds = Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    # Get existing tabs
    meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    existing_tabs = {s["properties"]["title"] for s in meta["sheets"]}

    slugs = load_cities_order()
    raw_data = load_all_data()

    # Build city metadata (city_id = position in cities.md, 1-indexed)
    city_meta = []  # (city_id, slug, city_name, state, country)
    for idx, slug in enumerate(slugs, 1):
        parts = slug.split("/")
        city_name = display_name(parts[-1])
        state = display_name(parts[1]) if len(parts) > 1 else ""
        country = display_name(parts[0]) if parts else ""
        city_meta.append((idx, slug, city_name, state, country))

    city_id_by_slug = {m[1]: m[0] for m in city_meta}

    # Load all daily entries per city
    # all_entries[slug] = [(date_str, aqi_val), ...]
    all_entries = {}
    for city_id, slug, city_name, state, country in city_meta:
        if slug not in raw_data:
            print(f"  WARNING: no data file for {slug}")
            all_entries[slug] = []
            continue
        payload = raw_data[slug].get("data", {})
        entries = payload.get("data", [])
        all_entries[slug] = [
            (e["day"], int(e["value"]))
            for e in entries
            if e.get("day") and e.get("value") is not None
        ]

    # 2026-only entries per city
    entries_2026 = {
        slug: [(d, v) for d, v in pairs if d.startswith("2026")]
        for slug, pairs in all_entries.items()
    }

    # ── dim_cities (existing) ────────────────────────────────────────────
    dim_cities = [["city_id", "slug", "city_name", "state", "country"]]
    for city_id, slug, city_name, state, country in city_meta:
        dim_cities.append([city_id, slug, city_name, state, country])
    clear_and_write(service, "dim_cities", dim_cities, existing_tabs)

    # ── dim_city (original tab — same data, different column order) ──────
    dim_city = [["city_id", "city", "state", "country", "slug"]]
    for city_id, slug, city_name, state, country in city_meta:
        dim_city.append([city_id, city_name, state, country, slug])
    clear_and_write(service, "dim_city", dim_city, existing_tabs)

    # ── dim_months (existing) ────────────────────────────────────────────
    dim_months = [["month_id", "month_name", "year"]]
    for i, name in enumerate(MONTH_NAMES, 1):
        dim_months.append([i, name, 2026])
    clear_and_write(service, "dim_months", dim_months, existing_tabs)

    # ── dim_date (all unique 2026 dates across all cities) ───────────────
    all_2026_dates = sorted({
        date_str
        for pairs in entries_2026.values()
        for date_str, _ in pairs
    })
    dim_date = [["date_key", "date", "year", "month_num", "month_name", "day"]]
    for d in all_2026_dates:
        month_num = int(d[5:7])
        dim_date.append([
            d.replace("-", ""),  # date_key YYYYMMDD
            d,
            2026,
            month_num,
            MONTH_NAMES[month_num - 1],
            int(d[8:10]),
        ])
    clear_and_write(service, "dim_date", dim_date, existing_tabs)

    # ── aqi_daily (existing) ─────────────────────────────────────────────
    aqi_daily = [["city_id", "date", "aqi", "aqi_category", "month_id"]]
    for city_id, slug, city_name, state, country in city_meta:
        for date_str, aqi_val in entries_2026[slug]:
            month_id = int(date_str[5:7])
            aqi_daily.append([city_id, date_str, aqi_val, aqi_category(aqi_val), month_id])
    clear_and_write(service, "aqi_daily", aqi_daily, existing_tabs)

    # ── fact_aqi_daily (date_key, city_id, aqi) ──────────────────────────
    fact_aqi_daily = [["date_key", "city_id", "aqi"]]
    for city_id, slug, city_name, state, country in city_meta:
        for date_str, aqi_val in entries_2026[slug]:
            fact_aqi_daily.append([date_str.replace("-", ""), city_id, aqi_val])
    clear_and_write(service, "fact_aqi_daily", fact_aqi_daily, existing_tabs)

    # ── Per-city computed stats (2026) ───────────────────────────────────
    # monthly_avg[slug][month_num] = avg AQI
    # current_aqi[slug] = most recent day's AQI
    monthly_avg = {}
    current_aqi = {}
    ytd_avg = {}

    for city_id, slug, city_name, state, country in city_meta:
        pairs = entries_2026[slug]
        if not pairs:
            monthly_avg[slug] = {}
            current_aqi[slug] = None
            ytd_avg[slug] = None
            continue

        by_month = defaultdict(list)
        for date_str, val in pairs:
            by_month[int(date_str[5:7])].append(val)

        monthly_avg[slug] = {m: round(statistics.mean(vals)) for m, vals in by_month.items()}
        current_aqi[slug] = sorted(pairs)[-1][1]  # latest date
        ytd_avg[slug] = round(statistics.mean(v for _, v in pairs))

    # ── fact_live_snapshot (city_id, current_aqi, pm25…) ─────────────────
    # pm25, pm10, temp_c, humidity_pct, world_rank not available from calendar API — left blank
    fact_live_snapshot = [["city_id", "current_aqi", "pm25", "pm10",
                           "temp_c", "humidity_pct", "world_rank"]]
    for city_id, slug, city_name, state, country in city_meta:
        fact_live_snapshot.append([
            city_id,
            current_aqi[slug] if current_aqi[slug] is not None else "",
            "", "", "", "", ""
        ])
    clear_and_write(service, "fact_live_snapshot", fact_live_snapshot, existing_tabs)

    # ── Dashboard ─────────────────────────────────────────────────────────
    dashboard = [
        ["AQI Dashboard (Scalable Structure)"],
        [],
        ["City", "Current AQI", "Status", "World Rank",
         "YTD Avg AQI", "Best Month", "Best AQI", "Worst Month", "Worst AQI"]
    ]
    for city_id, slug, city_name, state, country in city_meta:
        cur = current_aqi[slug]
        ytd = ytd_avg[slug]
        mavg = monthly_avg[slug]
        if cur is None:
            dashboard.append([city_name, "", "", "", "", "", "", "", ""])
            continue
        best_m = min(mavg, key=mavg.get) if mavg else None
        worst_m = max(mavg, key=mavg.get) if mavg else None
        dashboard.append([
            city_name,
            cur,
            aqi_category(cur),
            "",  # World Rank — not available
            ytd if ytd is not None else "",
            MONTH_NAMES[best_m - 1] if best_m else "",
            mavg[best_m] if best_m else "",
            MONTH_NAMES[worst_m - 1] if worst_m else "",
            mavg[worst_m] if worst_m else "",
        ])
    clear_and_write(service, "Dashboard", dashboard, existing_tabs)

    # ── City Summary ──────────────────────────────────────────────────────
    # PM2.5, PM10, Temp, Humidity, World Rank not in calendar data — left blank
    city_summary = [["City", "State", "Country", "Current AQI",
                     "PM2.5", "PM10", "Temp C", "Humidity %", "World Rank"]]
    for city_id, slug, city_name, state, country in city_meta:
        city_summary.append([
            city_name, state, country,
            current_aqi[slug] if current_aqi[slug] is not None else "",
            "", "", "", "", ""
        ])
    clear_and_write(service, "City Summary", city_summary, existing_tabs)

    # ── Monthly Data ──────────────────────────────────────────────────────
    monthly_data = [["City", "Month", "Average AQI"]]
    for city_id, slug, city_name, state, country in city_meta:
        for m in range(1, 13):
            if m in monthly_avg[slug]:
                monthly_data.append([city_name, MONTH_NAMES[m - 1], monthly_avg[slug][m]])
    clear_and_write(service, "Monthly Data", monthly_data, existing_tabs)

    # ── Daily Data ────────────────────────────────────────────────────────
    daily_data = [["Date", "City", "AQI"]]
    all_daily = []
    for city_id, slug, city_name, state, country in city_meta:
        for date_str, aqi_val in entries_2026[slug]:
            all_daily.append((date_str, city_name, aqi_val))
    all_daily.sort()  # by date
    daily_data.extend([d, c, v] for d, c, v in all_daily)
    clear_and_write(service, "Daily Data", daily_data, existing_tabs)

    # ── Annual Trends ─────────────────────────────────────────────────────
    annual_trends = [["City", "Year", "Average AQI"]]
    for city_id, slug, city_name, state, country in city_meta:
        by_year = defaultdict(list)
        for date_str, val in all_entries[slug]:
            by_year[date_str[:4]].append(val)
        for year in sorted(by_year):
            annual_trends.append([city_name, int(year), round(statistics.mean(by_year[year]))])
    clear_and_write(service, "Annual Trends", annual_trends, existing_tabs)

    print(f"\nAll tabs updated.")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    main()
