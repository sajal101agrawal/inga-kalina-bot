import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Authenticate
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Try to open the sheet
GOOGLE_SHEET_ID = "1KP8STQJ_eE-CBxLICD4eUD4t1rJbb-wSmO8dUtSZGzE"

try:
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Sheet1")
    print(f"✅ Successfully accessed sheet: {sheet.title}")
    
    prompt = sheet.acell('B2').value
        
    print(prompt)
except gspread.exceptions.SpreadsheetNotFound:
    print("❌ Google Sheet not found! Check the ID and permissions.")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
