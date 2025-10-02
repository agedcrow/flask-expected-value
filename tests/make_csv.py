import json
from pathlib import Path
from expected.visualize.spreadsheet import connect_gspread, ws2df


key = 'test_imarine'
csv_file = 'imarine.csv'

parent = Path(__file__).parent.parent
SSKEY_FILE = parent.joinpath('expected', 'visualize', 'secrets', 'sskey.json')
# print(Path.exists(SSKEY_FILE))
with open(SSKEY_FILE, 'r') as f:
    d = json.load(f)

    SSKEY = d[key]
    worksheets = connect_gspread(SSKEY)
    ws = worksheets[0]
    df = ws2df(ws)
    df.to_csv(parent.joinpath('tests', 'visualize', csv_file))