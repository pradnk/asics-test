Add a new city to the AQI data pipeline.

Usage: /add-city <slug>   (e.g. /add-city india/karnataka/mysuru)

## Steps

1. Validate the slug format — must follow `india/<state>/<city>`. Reject and explain if wrong.
2. Check `.claude/scripts/cities.md` — if the slug already exists, tell the user and stop.
3. Verify the slug is live: navigate to `https://www.aqi.in/dashboard/<slug>` and confirm the page loads (not a 404). If it 404s, suggest the likely correct slug and ask the user to confirm before adding.
4. Append the validated slug on a new line to `.claude/scripts/cities.md`.
5. Confirm: "Added `<slug>` to cities.md. Run `/run-aqi <slug>` to fetch its data."

## Key paths

| Purpose | Path |
|---|---|
| City list | `.claude/scripts/cities.md` |
| AQI data output | `.claude/scripts/data/aqi/` and `data/aqi/` |
