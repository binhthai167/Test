import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os, json
from google.oauth2.service_account import ServiceAccountCredentials

# Scope: quyền truy cập Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Đường dẫn file key json
SERVICE_ACCOUNT_FILE = "exam-result-system-7b9b00583bcf.json"

# ID của Google Sheet (lấy từ URL)
SPREADSHEET_ID = "1pTzsTRZBfM2gY1GDcEWafO5GadTSoDqRvJhVMP9hKHI"

def get_client():
    service_account_info = json.loads(os.environ["GOOGLE_CREDS"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client
def get_or_create_sheet(sheet_name):
    client = get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        # Nếu sheet đã tồn tại thì mở
        sheet = spreadsheet.worksheet(sheet_name)
        
    except gspread.exceptions.WorksheetNotFound:
        # Nếu chưa có thì tạo mới
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)
        # Thêm header ngay sau khi tạo
        headers = ["Họ và tên", "Số điện thoại", "Email", "Công ty cung ứng", "Biển số xe", "Điểm", "Kết quả", "Thời gian nộp", "Chi tiết kết quả"]
        sheet.update("A1:I1", [headers])
    return sheet

  
def append_exam_result(data):
    # Lấy tên sheet theo ngày hiện tại
    today = datetime.now().strftime("%Y-%m-%d")
    sheet = get_or_create_sheet(today)
    sheet.append_row(data, value_input_option="USER_ENTERED")
