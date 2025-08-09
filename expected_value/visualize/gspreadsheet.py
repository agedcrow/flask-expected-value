import gspread
from google.oauth2.service_account import Credentials
import json
import os


project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
instance_path = os.path.join(project_path, 'workspace/instance')
TOKEN_FILE = os.path.normpath(os.path.join(instance_path, 'token.json'))
SSKEY_FILE = os.path.normpath(os.path.join(instance_path, 'sskey.json'))


def connect_gspread(SPREADSHEET_KEY: str) -> list:

    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(TOKEN_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    
    return worksheets

def get_sskey():
    return json.load(open(SSKEY_FILE, 'r'))


if __name__ == "__main__":
    print(get_sskey())
    # project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # instance_path = os.path.join(project_path, 'instance')
    # JSON_FILE = os.path.normpath(os.path.join(instance_path, 'token.json'))
    # print(JSON_FILE)
