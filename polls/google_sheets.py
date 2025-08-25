import gspread
from google.oauth2.service_account import Credentials
from django.utils import timezone
import os, json


# Scope: quyền truy cập Google Sheets
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

# Đường dẫn file key json
SERVICE_ACCOUNT_FILE = "exam-result-system-7b9b00583bcf.json"

# ID của Google Sheet (lấy từ URL)
SPREADSHEET_ID = "1pTzsTRZBfM2gY1GDcEWafO5GadTSoDqRvJhVMP9hKHI"

def get_client():
    service_account_info = json.loads(os.environ["GOOGLE_CREDS"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client
def get_or_create_file():
    client = get_client()
    today = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
    file_name = f"Exam Results {today}"
    folder_id = "1n7BTwkuiVFj-1Iz9ZPg8EOAshE9P6PrS" 
    try:
        # Nếu sheet đã tồn tại thì mở
        spreadsheet = client.create(file_name, folder_id=folder_id)
        
    except gspread.exceptions.WorksheetNotFound:
       # Nếu chưa có thì tạo mới
        spreadsheet = client.create(file_name)
        sheet = spreadsheet.sheet1
        headers = ["Họ và tên", "Số điện thoại", "Email", "Công ty cung ứng",
                   "Biển số xe", "Điểm", "Kết quả", "Thời gian nộp", "Chi tiết kết quả"]
        sheet.update("A1:I1", [headers])
    return spreadsheet

  
def append_exam_result(data):
    # Lấy tên sheet theo ngày hiện tại
    spreadsheet = get_or_create_file()
    sheet = spreadsheet.sheet1
    sheet.append_row(data, value_input_option="USER_ENTERED")
