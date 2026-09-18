import gspread
from google.oauth2.service_account import Credentials
from datetime import timezone
import os, json


# Scope: quyền truy cập Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Đường dẫn file key json
SERVICE_ACCOUNT_FILE = "exam-result-system-d8f57ca5d189.json"

# ID của Google Sheet (lấy từ URL)
SPREADSHEET_ID = "1pTzsTRZBfM2gY1GDcEWafO5GadTSoDqRvJhVMP9hKHI"

def get_client():
    # 1. Comment hoặc xoá 2 dòng đọc biến môi trường này đi
    # service_account_info = json.loads(os.environ["GOOGLE_CREDS"])
    # creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    
    # 2. Mở comment (bỏ dấu #) ở dòng dưới đây để đọc trực tiếp từ file JSON của bạn
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    client = gspread.authorize(creds)
    return client

# def get_client():
#     service_account_info = json.loads(os.environ["GOOGLE_CREDS"])
#     creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
#     # creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     client = gspread.authorize(creds)
#     return client


# THÊM THAM SỐ sheet_name VÀO HÀM NÀY
def append_exam_result(data, sheet_name="Đầu vào"):
    client = get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    
    try:
        # Tìm tab theo tên (ví dụ: "Đầu vào" hoặc "Đầu ra")
        sheet = spreadsheet.worksheet(sheet_name)
    except Exception:
        # Nếu không tìm thấy tên tab (do chưa tạo hoặc gõ sai tên), mặc định lấy tab đầu tiên
        sheet = spreadsheet.sheet1  
        
    sheet.insert_row(data, 2, value_input_option="USER_ENTERED")