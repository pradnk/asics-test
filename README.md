# ASICS — India City Data Intelligence Platform

ASICS is a Claude Code-powered toolkit for collecting, validating, and publishing city-level data for Indian cities — air quality (AQI), government statistics (MOSPI), and automated RTI applications for data that doesn't yet exist publicly.

**The goal:** Authoritatively say "this data is true" — and when it isn't available, generate a legally valid RTI application to demand it.

---

## What's in this repo

| Component | What it does |
|---|---|
| **AQI Pipeline** | Fetches daily air quality index data for tracked cities, stores it as JSON, and pushes to Google Sheets |
| **MOSPI Pipeline** | Pulls environmental indicator data from the Ministry of Statistics (MOSPI) API |
| **RTI Generator** | Generates a ready-to-submit RTI application under the RTI Act 2005 as a `.docx` file |

All three are driven by Claude Code slash commands and skills — no separate CLI tools needed.

---

## Prerequisites

### 1. Claude Code
Install Claude Code and open this folder as your project. The `.claude/` directory already has all commands and skills wired up.

### 2. One-time launchd setup (macOS)

The AQI and MOSPI pipelines use macOS `launchd` to run Python scripts (Claude's sandbox blocks outbound network calls). Run these once in Terminal:

```bash
# AQI pipeline
cp /Users/pradeep/Work/asics-test/.claude/scripts/org.asics.aqi-fetch.plist \
   ~/Library/LaunchAgents/org.asics.aqi-fetch.plist
launchctl load ~/Library/LaunchAgents/org.asics.aqi-fetch.plist

# MOSPI pipeline
cp /Users/pradeep/Work/asics-test/.claude/scripts/org.asics.mospi-fetch.plist \
   ~/Library/LaunchAgents/org.asics.mospi-fetch.plist
launchctl load ~/Library/LaunchAgents/org.asics.mospi-fetch.plist
```

To verify:
```bash
launchctl list | grep asics
```

### 3. Google Sheets access
The service account key must be at `~/keys/sheets-key.json` and already have Editor access on the [AQI Google Sheet](https://docs.google.com/spreadsheets/d/1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ/edit).

### 4. Node.js (for RTI)
```bash
npm install -g docx
```

---

## Commands

### AQI Pipeline

#### `/add-city <slug>`
Add a new Indian city to the AQI tracking list.

The slug must follow the format `india/<state>/<city>`.

```
/add-city india/karnataka/mysuru
/add-city india/maharashtra/nagpur
```

What happens:
1. Validates the slug format
2. Checks it isn't already tracked
3. Verifies the city page is live on aqi.in
4. Appends it to `.claude/scripts/cities.md`

**Cities currently tracked:** Bangalore, Mysuru, Madikeri, Hubballi, Bidar, Belagavi, Mumbai, New Delhi, Panaji, Pune, Hyderabad, Jaipur

---

#### `/run-aqi [slug]`
Fetch AQI calendar data and push everything to Google Sheets.

```
/run-aqi                          # runs for all cities
/run-aqi india/karnataka/mysuru   # runs for one city only
```

What happens:
1. Triggers the launchd job (touches `.run_trigger`)
2. Polls `.run_done` every 5 seconds (3-minute timeout)
3. Reads `run.log` for results
4. Handles 404s gracefully — tries common slug corrections before flagging to you
5. Prints a summary and a link to the sheet

Data is saved to `.claude/scripts/data/aqi/<state>/<city>.json` and mirrored to `data/aqi/`.

---

#### `/refresh-sheets`
Push existing local AQI JSON files to Google Sheets without re-fetching from the API.

```
/refresh-sheets
```

Use this when you have fresh JSON locally but just need to update the sheet (faster than a full `/run-aqi`). Uses the same launchd trigger mechanism.

**Tabs written to the sheet:**

| Tab | Contents |
|---|---|
| `dim_cities` / `dim_city` | Master city list with IDs |
| `dim_months` / `dim_date` | Date dimension tables (all of 2026) |
| `aqi_daily` / `fact_aqi_daily` | Daily AQI readings per city |
| `fact_live_snapshot` | Latest AQI snapshot per city |
| `Dashboard` | Summary: current AQI, YTD avg, best/worst month |
| `City Summary` | Current AQI by city |
| `Monthly Data` | Monthly averages |
| `Daily Data` | All daily rows sorted by date |
| `Annual Trends` | Year-on-year averages (2020+) |

---

#### `/check-cities`
Validate every city slug in `cities.md` and report which are live, redirected, or broken.

```
/check-cities
```

Outputs a table like:

| City | Status |
|---|---|
| india/karnataka/bangalore | ✅ Live |
| india/maharashtra/mumbai | ✅ Live |
| india/old/slug | ❌ 404 — suggest: india/new/slug |

Claude will ask if you want to auto-fix any 404s and update `cities.md` in place.

---

### MOSPI Pipeline

#### `/run-mospi`
Fetch all environmental indicator data from India's Ministry of Statistics (MOSPI) API.

```
/run-mospi
```

What happens:
1. Triggers the launchd job (touches `.mospi_trigger`)
2. Polls `.mospi_done` every 5 seconds (5-minute timeout — up to 130 indicators at ~1s each)
3. Reads `run.log` for results
4. Writes one JSON file per indicator to `data/mospi/`

The script automatically stops when it hits an empty API response — no manual limit needed.

---

### RTI Generator

#### `/rti <description>`
Generate a ready-to-submit RTI application under Section 6(1) of the RTI Act 2005.

```
/rti Who were the contractors for MG Road, Bengaluru for the last 10 years
/rti Expenditure on Aarogya Setu scheme implementation in Karnataka 2020-2023
/rti Building approval status for Survey No. 45, Whitefield, Bengaluru
```

What happens:
1. Parses your description to identify what records you want, which department holds them, and the relevant time period
2. Maps to the correct public authority (PWD, BBMP, Revenue Dept, etc.)
3. Asks for your applicant details (name, address, mobile, email) — or use `/rti ... use placeholders`
4. Generates 5–8 specific, document-focused RTI questions (records and copies, never "why/how")
5. Produces a `.docx` file ready to submit

**RTI fee:** ₹10 for Central government authorities. State fees vary — confirm with your state's schedule.

**Department mapping (common subjects):**

| Subject | Authority |
|---|---|
| Roads, bridges, footpaths | PWD / Municipal Corporation Roads Dept |
| Water supply, drainage | Municipal Corporation / Water Board |
| Building permits, land use | BBMP / Development Authority |
| Government contracts | Concerned dept + District Collector |
| Schools, education | State Education Dept / DEO |
| Land records | Revenue Dept / Sub-Registrar |
| Central schemes | Relevant Ministry / Collectorate |

If the subject spans multiple departments, Claude includes a **Section 6(3) transfer clause** so the application can be forwarded automatically.

---

## How the data pipeline works

```
You type a command
       │
       ▼
Claude touches a trigger file
  (.run_trigger or .mospi_trigger)
       │
       ▼
macOS launchd detects the change
and runs the Python/shell script
       │
       ▼
Script fetches data from the web
(aqi.in API or MOSPI API)
saves JSON to data/
       │
       ▼
Script pushes to Google Sheets
writes exit code to done file
       │
       ▼
Claude polls done file, reads log,
reports results to you
```

This indirection (trigger file → launchd → script) exists because Claude's sandbox blocks outbound network access. The script runs directly on your Mac where network is available.

---

## File structure

```
.claude/
├── commands/          # Slash command definitions
│   ├── add-city.md
│   ├── check-cities.md
│   ├── refresh-sheets.md
│   ├── rti.md
│   ├── run-aqi.md
│   └── run-mospi.md
├── skills/            # AI skill definitions
│   ├── aqi-SKILL.md
│   ├── mospi-SKILL.md
│   └── rti-SKILL.md
├── scripts/           # Python + Node scripts
│   ├── cities.md                    # One slug per line
│   ├── get_token_parse_aqi.py       # AQI fetch script
│   ├── fetch_mospi_data.py          # MOSPI fetch script
│   ├── refresh_sheets.py            # Google Sheets push
│   ├── generate_rti_application.js  # RTI .docx generator
│   ├── org.asics.aqi-fetch.plist    # launchd job (AQI)
│   ├── org.asics.mospi-fetch.plist  # launchd job (MOSPI)
│   ├── .run_trigger / .run_done     # AQI pipeline signals
│   ├── .mospi_trigger / .mospi_done # MOSPI pipeline signals
│   └── run.log                      # Shared log
└── assets/
    └── rti_template.md              # RTI document boilerplate

data/
├── aqi/               # Daily AQI JSON per city
└── mospi/             # One JSON per MOSPI indicator
```

---

## AQI category reference

| AQI Range | Category | Meaning |
|---|---|---|
| 0–50 | Good | Air quality is satisfactory |
| 51–100 | Moderate | Acceptable for most people |
| 101–150 | Poor | Sensitive groups may be affected |
| 151–200 | Unhealthy | Everyone may experience effects |
| 201–300 | Severe | Health warnings |
| 301+ | Hazardous | Emergency conditions |

---

## Troubleshooting

**launchd job never completes (`.run_done` never appears)**
The plist may not be loaded. See Prerequisites → launchd setup above.

**City page 404s after `/run-aqi`**
Claude will try common corrections (e.g. `belgaum` → `belagavi`). If none work, it will flag the city and skip it. Run `/check-cities` for a full audit.

**RTI docx generation fails**
Ensure Node.js is installed and `docx` is globally available:
```bash
npm install -g docx
node --version
```

**Google Sheets not updating**
Check that `~/keys/sheets-key.json` exists and the service account email has Editor access on the sheet.
