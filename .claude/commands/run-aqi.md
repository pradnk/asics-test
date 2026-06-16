Fetch AQI calendar data for all cities (or a specific city) and push to Google Sheets.

Usage: /run-aqi          — runs for all cities in cities.md
       /run-aqi <slug>   — runs for one city only (e.g. /run-aqi india/karnataka/mysuru)

## Execution model

All network access must run on the Mac via launchd — never run the Python script directly from the sandbox (network is blocked there).

1. Touch `.claude/scripts/.run_trigger` to fire the launchd job.
2. Poll `.claude/scripts/.run_done` every 5 seconds until its mtime is newer than the trigger's mtime. Timeout after 3 minutes.
3. Read `.claude/scripts/run.log` (last 20 lines) to verify completion and catch errors.
4. Print a summary: cities fetched, cities fixed, cities skipped, and a link to the sheet.

## Handling 404s

If a city page returns 404, do NOT delete it from cities.md. Instead:
- Try common slug corrections (e.g. `belgaum` → `belagavi`, `delhi` → `delhi/new-delhi`)
- If a correction works, update the slug in `.claude/scripts/cities.md` (edit in place)
- Log the correction: "Fixed: `<old>` → `<new>`"
- If no correction can be found, flag it to the user and skip that city

## Key paths

| Purpose | Path |
|---|---|
| Trigger file | `.claude/scripts/.run_trigger` |
| Done marker | `.claude/scripts/.run_done` |
| Log | `.claude/scripts/run.log` |
| Shell wrapper | `.claude/scripts/run_aqi.sh` |
| launchd plist | `.claude/scripts/org.asics.aqi-fetch.plist` |
| City list | `.claude/scripts/cities.md` |
| Data output | `.claude/scripts/data/aqi/<state>/<city>.json` (mirrored to `data/aqi/`) |
| Google Sheet | https://docs.google.com/spreadsheets/d/1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ/edit |

## First-time launchd setup

If `.run_done` never appears after triggering, the plist may not be loaded. Ask the user to run once in Terminal:

```bash
cp /Users/pradeep/Work/asics-test/.claude/scripts/org.asics.aqi-fetch.plist \
   ~/Library/LaunchAgents/org.asics.aqi-fetch.plist
launchctl load ~/Library/LaunchAgents/org.asics.aqi-fetch.plist
```
