#!/bin/bash
# Triggered by launchd WatchPaths (via .mospi_trigger) or on-demand.
# Runs fetch_mospi_data.py and logs output to run.log.

SCRIPT_DIR="/Users/pradeep/Work/asics-test/.claude/scripts"
TRIGGER="$SCRIPT_DIR/.mospi_trigger"
DONE_FILE="$SCRIPT_DIR/.mospi_done"
LOG="$SCRIPT_DIR/run.log"

cd "$SCRIPT_DIR" || exit 1

# Remove stale done-marker so Claude knows a fresh run is in progress
rm -f "$DONE_FILE"

echo "[$(date)] Starting MOSPI fetch..." >> "$LOG"
python3 fetch_mospi_data.py >> "$LOG" 2>&1
STATUS=$?

# Write done-marker with exit status so Claude can detect completion
echo "$STATUS" > "$DONE_FILE"
echo "[$(date)] MOSPI fetch done (exit $STATUS)" >> "$LOG"
