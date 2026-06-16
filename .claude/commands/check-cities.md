Validate every city slug in cities.md and report which are live, redirected, or 404.

## Steps

1. Read all slugs from `.claude/scripts/cities.md`.
2. For each slug, check `https://www.aqi.in/dashboard/<slug>`.
3. Classify each as:
   - ✅ **Live** — page loads correctly
   - ⚠️ **Redirected** — loads but URL changed (note the final URL)
   - ❌ **404** — page not found (suggest a corrected slug if possible)
4. Print a table with all results.
5. Ask the user: "Want me to auto-fix the 404s and update cities.md?"
   If yes, apply corrections (edit in place, never delete) and confirm each change.

## Key paths

| Purpose | Path |
|---|---|
| City list | `.claude/scripts/cities.md` |
