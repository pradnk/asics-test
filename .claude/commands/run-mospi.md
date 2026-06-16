Fetch all MOSPI environmental indicator data using the launchd pipeline.

## Execution model

All network access must run on the Mac via launchd — never run the Python script directly from the sandbox (network is blocked there).

Steps:
1. Touch `.claude/scripts/.mospi_trigger` to fire the launchd job (e.g. `touch /Users/pradeep/Work/asics-test/.claude/scripts/.mospi_trigger` via the Write tool or Bash).
2. Poll `.claude/scripts/.mospi_done` every 5 seconds until its mtime is newer than the trigger's mtime. Timeout after 5 minutes.
3. Read `.claude/scripts/run.log` (last 20 lines) to verify completion and catch errors.
4. Report: how many JSON files were written, any errors, exit code from `.mospi_done`.

## Key paths

| Purpose | Path |
|---|---|
| Script | `.claude/scripts/fetch_mospi_data.py` |
| Shell wrapper | `.claude/scripts/run_mospi.sh` |
| launchd plist | `.claude/scripts/org.asics.mospi-fetch.plist` |
| Trigger file | `.claude/scripts/.mospi_trigger` |
| Done marker | `.claude/scripts/.mospi_done` |
| Log | `.claude/scripts/run.log` |
| Data output | `data/mospi/` (one JSON per indicator, named by indicator field) |

## First-time launchd setup

If `.mospi_done` never appears after triggering, the plist may not be loaded. Ask the user to run once in Terminal:

```bash
cp /Users/pradeep/Work/asics-test/.claude/scripts/org.asics.mospi-fetch.plist \
   ~/Library/LaunchAgents/org.asics.mospi-fetch.plist
launchctl load ~/Library/LaunchAgents/org.asics.mospi-fetch.plist
```
