---
name: mospi
description: >
  MOSPI environmental statistics pipeline for the asics-test project. Use this skill
  whenever the user runs /run-mospi or uses equivalent natural language like
  "fetch MOSPI data", "refresh MOSPI indicators", or "run the MOSPI script".
  Always use this skill for any task involving fetch_mospi_data.py or the
  data/mospi/ directory.
---

# MOSPI Workflow

This skill orchestrates the MOSPI environmental statistics pipeline for the asics-test project.

- Script: `.claude/scripts/fetch_mospi_data.py`
- Shell wrapper: `.claude/scripts/run_mospi.sh`
- launchd plist: `.claude/scripts/org.asics.mospi-fetch.plist`
- Data output: `data/mospi/` (one JSON per indicator, named after the indicator field)
- Trigger file: `.claude/scripts/.mospi_trigger`
- Done marker: `.claude/scripts/.mospi_done`
- Log: `.claude/scripts/run.log`

---

## Execution model — IMPORTANT

All network access must run on the Mac, not in the Claude sandbox (sandbox network is blocked).
The launchd job handles this:

1. Claude touches `.claude/scripts/.mospi_trigger`
2. launchd detects the file change and runs `run_mospi.sh` on the Mac
3. `run_mospi.sh` runs `fetch_mospi_data.py`, which iterates indicator_code 1–130,
   stops on empty/error, and writes one JSON per indicator to `data/mospi/`
4. On completion, the script writes the exit code to `.mospi_done`
5. Claude polls `.mospi_done` (checking mtime > mtime of `.mospi_trigger`) to detect completion
6. Claude reads `run.log` to verify results

**Never** run `fetch_mospi_data.py` directly from the sandbox — it will fail with 403/tunnel errors.

---

## First-time launchd setup

If the job has not been loaded yet, ask the user to run these commands once in Terminal:

```bash
cp /Users/pradeep/Work/asics-test/.claude/scripts/org.asics.mospi-fetch.plist \
   ~/Library/LaunchAgents/org.asics.mospi-fetch.plist

launchctl load ~/Library/LaunchAgents/org.asics.mospi-fetch.plist
```

To verify it loaded:
```bash
launchctl list | grep mospi
```

---

## Commands

### `/run-mospi`

Fetch all MOSPI environmental indicator data and save to `data/mospi/`.

1. Touch `.claude/scripts/.mospi_trigger` to kick off the launchd job.
2. Poll `.claude/scripts/.mospi_done` every 5 seconds until its mtime > trigger mtime (timeout ~5 min — the script fetches up to 130 indicators with a 1s delay each).
3. Read `.claude/scripts/run.log` to confirm results and catch any errors.
4. Report: how many JSON files were written, any errors encountered.

The script stops automatically when it hits an empty response, so it gracefully handles
the API having fewer than 130 indicators.

---

## File layout reference

```
.claude/scripts/
├── fetch_mospi_data.py          # Main fetch script
├── run_mospi.sh                 # Shell wrapper invoked by launchd
├── org.asics.mospi-fetch.plist  # launchd job definition
├── .mospi_trigger               # Touch this to fire a run
├── .mospi_done                  # Exit code written here on completion
└── run.log                      # Shared log (appended by all pipeline scripts)

data/
└── mospi/
    ├── <indicator_name>.json    # One file per indicator
    └── ...
```
