import gspread
from google.oauth2.service_account import Credentials
from datetime import timezone
import os, json


# Scope: quyền truy cập Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Đường dẫn file key json
SERVICE_ACCOUNT_FILE = "exam-result-system-7b9b00583bcf.json"

# ID của Google Sheet (lấy từ URL)
SPREADSHEET_ID = "1pTzsTRZBfM2gY1GDcEWafO5GadTSoDqRvJhVMP9hKHI"

def get_client():
    service_account_info = json.loads(os.environ["GOOGLE_CREDS"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    # creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def append_exam_result(data):
    client = get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.sheet1  # sheet đầu tiên
    sheet.insert_row(data, 2, value_input_option="USER_ENTERED")
