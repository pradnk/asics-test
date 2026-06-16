#!/usr/bin/env python3
"""Read existing tab structures from Google Sheets and dump to JSON."""
import json
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1ptt1Lye__zLQQB-3_wAASvMsaoJsXYAmWLsws078DtQ"
SCRIPT_DIR = Path(__file__).parent
KEY_FILE = SCRIPT_DIR / "keys" / "sheets-key.json"
OUT_FILE = SCRIPT_DIR / "tab_structures.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TABS = ["Dashboard", "City Summary", "Monthly Data", "Daily Data",
        "Annual Trends", "dim_city", "dim_date", "fact_aqi_daily", "fact_live_snapshot"]

creds = Credentials.from_service_account_file(str(KEY_FILE), scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)

result = {}
for tab in TABS:
    data = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{tab}'!A1:Z100"
    ).execute()
    result[tab] = data.get("values", [])
    print(f"  {tab}: {len(result[tab])} rows")

with open(OUT_FILE, "w") as f:
    json.dump(result, f, indent=2)
print(f"\nSaved to {OUT_FILE}")
