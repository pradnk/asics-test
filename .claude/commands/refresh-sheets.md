Push existing local AQI JSON data to Google Sheets without re-fetching from the AQI API.

## Execution model

Runs via the same launchd trigger as /run-aqi — touch `.run_trigger`, poll `.run_done`.

1. Touch `.claude/scripts/.run_trigger` to fire the launchd job.
2. Poll `.claude/scripts/.run_done` every 5 seconds until its mtime is newer than the trigger's mtime. Timeout after 3 minutes.
3. Read `.claude/scripts/run.log` (last 20 lines) to verify completion.
4. Confirm with a link to the sheet when done.

## Sheet details

Sheet: https://docs.google.com/spreadsheets/d/1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ/edit
Service account key: `~/keys/sheets-key.json` (already shared as Editor on the sheet)
Script: `.claude/scripts/refresh_sheets.py`

All tabs are overwritten on each run (full replace, not append). City IDs come from the order in `cities.md` (1-indexed).

## Tabs written

| Tab | Columns | Source |
|-----|---------|--------|
| `dim_cities` | city_id, slug, city_name, state, country | cities.md order |
| `dim_city` | city_id, city, state, country, slug | same, different column order |
| `dim_months` | month_id, month_name, year | static (Jan–Dec 2026) |
| `dim_date` | date_key, date, year, month_num, month_name, day | all unique 2026 dates |
| `aqi_daily` | city_id, date, aqi, aqi_category, month_id | 2026 daily data |
| `fact_aqi_daily` | date_key, city_id, aqi | 2026 daily data |
| `fact_live_snapshot` | city_id, current_aqi, pm25…world_rank | latest AQI; pm25/pm10/temp/humidity/rank=blank |
| `Dashboard` | City, Current AQI, Status, World Rank, YTD Avg, Best/Worst Month | computed from 2026 |
| `City Summary` | City, State, Country, Current AQI, PM2.5… | current AQI; PM/temp/humidity=blank |
| `Monthly Data` | City, Month, Average AQI | 2026 monthly averages |
| `Daily Data` | Date, City, AQI | all 2026 daily rows sorted by date |
| `Annual Trends` | City, Year, Average AQI | all available years (2020+) |

## Data shape

JSON files: `d["data"]["data"]` → flat list of `{"day": "YYYY-MM-DD", "value": N}`
City display names: title-cased from slug (e.g. `new-delhi` → `New Delhi`)
Not available from calendar API: PM2.5, PM10, temperature, humidity, world rank — left blank

## AQI category thresholds (AQI-US)

| Range | Category |
|-------|----------|
| 0–50 | Good |
| 51–100 | Moderate |
| 101–150 | Poor |
| 151–200 | Unhealthy |
| 201–300 | Severe |
| 301+ | Hazardous |
