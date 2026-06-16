---
name: aqi
description: >
  AQI data pipeline workflow for the asics-test project. Use this skill whenever
  the user runs any of these commands: /add-city, /run-aqi, /refresh-sheets,
  /check-cities — or uses equivalent natural language like "add a new city to
  the AQI list", "run the AQI parse", "update the Google Sheet with AQI data",
  or "check which cities are 404ing". Always use this skill for any task
  involving the cities.md city list, the AQI data pipeline scripts, or the
  AQI Google Sheet.
---

# AQI Workflow

This skill orchestrates the AQI data pipeline for the asics-test project.
All scripts live in `../scripts/` relative to this skill's directory.
All data outputs go to `../scripts/data/aqi/`.
The city list lives at `../scripts/cities.md`.

---

## Commands

### `/add-city <slug>`

Add a new city to the pipeline.

1. Validate the slug format — must follow `india/<state>/<city>` (e.g. `india/karnataka/mysuru`).
   Reject and explain if the format is wrong.
2. Check `../scripts/cities.md` — if the slug already exists, tell the user and stop.
3. Verify the slug is live: navigate to `https://www.aqi.in/dashboard/<slug>` and confirm
   the page loads (not a 404). If it 404s, suggest the likely correct slug (e.g. search
   for the city name on aqi.in) and ask the user to confirm before adding.
4. Append the validated slug on a new line to `../scripts/cities.md`.
5. Confirm: "Added `<slug>` to cities.md. Run `/run-aqi <slug>` to fetch its data."

---

## Execution model — IMPORTANT

All network access (aqi.in API, Google Sheets API) must run on the Mac, not in the Claude
sandbox. The sandbox network is blocked. The launchd job handles this:

1. Claude writes (touches) `.run_trigger` in `../scripts/`
2. launchd detects the file change and runs `../scripts/run_aqi.sh` on the Mac
3. `run_aqi.sh` runs `get_token_parse_aqi.py` (AQI fetch) then `refresh_sheets.py` (Sheets push)
4. On completion it writes exit code to `.run_done`
5. Claude polls `.run_done` (checking mtime > mtime of `.run_trigger`) to detect completion
6. Claude reads `../scripts/run.log` to check results

**Never** try to run the Python scripts directly from the sandbox — they will fail with 403/tunnel errors.

---

### `/run-aqi [slug]`

Fetch AQI calendar data and push to Google Sheets.

If a specific `slug` is given, run only for that city. Otherwise run for all cities in
`../scripts/cities.md`.

1. Touch `../scripts/.run_trigger` to kick off the launchd job (see Execution model above).
2. Poll `../scripts/.run_done` every 5 seconds until its mtime > trigger mtime (timeout ~3 min).
3. Read `../scripts/run.log` to confirm results and catch any errors.
4. **Handle 404s**: If a city page returns 404, do not delete it from cities.md. Instead:
   - Try common slug corrections (e.g. `belgaum` → `belagavi`, `delhi` → `delhi/new-delhi`)
   - If a correction works, update the slug in `../scripts/cities.md` (edit in place)
   - Log the correction: "Fixed: `<old>` → `<new>`"
   - If no correction can be found, flag it to the user and skip that city
3. JSON files are saved automatically by the script to `../scripts/data/aqi/<state>/<city>.json`
   (and mirrored to `../../data/aqi/`).
4. The Sheets push runs automatically as part of the same launchd job.
5. Print a summary: cities fetched, cities fixed, cities skipped, and a link to the sheet.

---

### `/refresh-sheets`

Push existing local JSON data to Google Sheets without re-fetching from the AQI API.

Runs via the same launchd trigger (touch `.run_trigger`, poll `.run_done`). The script
`../scripts/refresh_sheets.py` handles the push directly.

Sheet: `https://docs.google.com/spreadsheets/d/1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ/edit`
Service account key: `../scripts/keys/sheets-key.json` (already shared as Editor on the sheet)

All tabs are overwritten on each run (full replace, not append). City IDs come from the order
in `cities.md` (1-indexed). The script is `../scripts/refresh_sheets.py`.

**Tabs written and their source:**

| Tab | Columns | Source |
|-----|---------|--------|
| `dim_cities` | city_id, slug, city_name, state, country | cities.md order |
| `dim_city` | city_id, city, state, country, slug | same, different column order |
| `dim_months` | month_id, month_name, year | static (Jan–Dec 2026) |
| `dim_date` | date_key, date, year, month_num, month_name, day | all unique 2026 dates |
| `aqi_daily` | city_id, date, aqi, aqi_category, month_id | 2026 daily data |
| `fact_aqi_daily` | date_key, city_id, aqi | 2026 daily data |
| `fact_live_snapshot` | city_id, current_aqi, pm25…world_rank | latest AQI; pm25/pm10/temp/humidity/rank=blank (not in API) |
| `Dashboard` | City, Current AQI, Status, World Rank, YTD Avg, Best/Worst Month | computed from 2026 |
| `City Summary` | City, State, Country, Current AQI, PM2.5… | current AQI; PM/temp/humidity=blank |
| `Monthly Data` | City, Month, Average AQI | 2026 monthly averages |
| `Daily Data` | Date, City, AQI | all 2026 daily rows sorted by date |
| `Annual Trends` | City, Year, Average AQI | all available years (2020+) |

**Data shape in JSON files:** `d["data"]["data"]` → flat list of `{"day": "YYYY-MM-DD", "value": N}`
**City display names:** title-cased from slug (e.g. `new-delhi` → `New Delhi`)
**Not available from calendar API:** PM2.5, PM10, temperature, humidity, world rank — left blank
5. **dim_ tabs** (dimension tables — used for warehouse ingestion):
   - `dim_cities`: one row per city. Assign a stable integer `city_id` starting from 1,
     ordered by the city's position in `../scripts/cities.md`. Include: `city_id`, `slug`,
     `city_name`, `state`, `country`.
   - `dim_months`: month_id (1–12), month_name, year.
6. **Fact tab** (`aqi_daily`): one row per city per day with columns:
   `city_id`, `date` (YYYY-MM-DD), `aqi`, `aqi_category`, `month_id`.
7. Confirm with a link to the sheet when done.

AQI category thresholds (AQI-US):
| Range   | Category   |
|---------|------------|
| 0–50    | Good       |
| 51–100  | Moderate   |
| 101–150 | Poor       |
| 151–200 | Unhealthy  |
| 201–300 | Severe     |
| 301+    | Hazardous  |

---

### `/check-cities`

Validate every slug in `../scripts/cities.md` and report status.

1. For each slug in cities.md, check `https://www.aqi.in/dashboard/<slug>`.
2. Classify each as:
   - ✅ **Live** — page loads correctly
   - ⚠️ **Redirected** — loads but URL changed (note the final URL)
   - ❌ **404** — page not found (suggest a corrected slug if possible)
3. Print a table with all results.
4. Ask the user: "Want me to auto-fix the 404s and update cities.md?"
   If yes, apply corrections (edit in place, never delete) and confirm each change.

---

## File layout reference

```
scripts/
├── get_token_parse_aqi.py   # Main fetch script
├── cities.md                # One slug per line, e.g. india/karnataka/bangalore
└── data/
    └── aqi/
        ├── bangalore.json
        └── mysuru.json
```
