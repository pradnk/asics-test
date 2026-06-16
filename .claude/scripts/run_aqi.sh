#!/bin/bash
# Triggered by launchd WatchPaths (via .run_trigger) or daily cron.
# Runs from the scripts directory, logs to /tmp/aqi_run.log.

SCRIPT_DIR="/Users/pradeep/Work/asics-test/.claude/scripts"
TRIGGER="$SCRIPT_DIR/.run_trigger"
DONE_FILE="$SCRIPT_DIR/.run_done"

cd "$SCRIPT_DIR" || exit 1

# Remove stale done-marker so Claude knows a fresh run is in progress
rm -f "$DONE_FILE"

LOG="$SCRIPT_DIR/run.log"

# One-off helper tasks (triggered by special marker files)
if [ -f "$SCRIPT_DIR/.read_tabs_trigger" ]; then
  rm -f "$SCRIPT_DIR/.read_tabs_trigger"
  echo "[$(date)] Reading tab structures..." >> "$LOG"
  python3 read_tabs.py >> "$LOG" 2>&1
  STATUS=$?
  echo "$STATUS" > "$DONE_FILE"
  echo "[$(date)] Done (exit $STATUS)" >> "$LOG"
  exit $STATUS
fi

echo "[$(date)] Starting AQI fetch..." >> "$LOG"
python3 get_token_parse_aqi.py >> "$LOG" 2>&1
STATUS=$?

if [ "$STATUS" -eq 0 ]; then
  echo "[$(date)] Starting Sheets push..." >> "$LOG"
  python3 -c "import google.oauth2" 2>/dev/null || pip3 install google-auth google-api-python-client --quiet >> "$LOG" 2>&1
  python3 refresh_sheets.py >> "$LOG" 2>&1
  STATUS=$?
  echo "[$(date)] Sheets push done (exit $STATUS)" >> "$LOG"
fi

# Write done-marker with exit status so Claude can detect completion
echo "$STATUS" > "$DONE_FILE"
echo "[$(date)] Done (exit $STATUS)" >> "$LOG"
