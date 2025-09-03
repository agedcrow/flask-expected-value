import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import pandas as pd
import json
import os

import base64
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import re
import math


TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'secrets/token.json')
SSKEY_FILE = os.path.join(os.path.dirname(__file__), 'secrets/sskey.json')


def connect_gspread(SPREADSHEET_KEY: str) -> list:

    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(TOKEN_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    
    return worksheets


def get_sskey(machine_name: str) -> str:
    d = {}
    with open(SSKEY_FILE, 'r') as f:
        d = json.load(f)
    try:
        spreadsheet_key = d[machine_name]
        return spreadsheet_key
    except KeyError as e:
        print(f'get_sskey error: {e}')
        return ''


def get_all_records(spreadsheet_key: str, col_count=7) -> pd.DataFrame:
    worksheets = connect_gspread(spreadsheet_key)
    ws = worksheets[0]
    df = pd.DataFrame(ws.get_all_records())

    
    return df


def cutout(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sr = df['start']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    start = sr_numeric.dropna().to_numpy()

    sr = df['round']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    round_ = sr_numeric.dropna().astype(int).to_numpy()

    sr = df['payout']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    payout = sr_numeric.dropna().to_numpy()

    sr = df['game']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    game = sr_numeric.dropna().astype(int).to_numpy()

    # if not (round_.size == payout.size == game.size):
    #     print('oh!')

    return start, round_, payout, game


def get_rate(start: float, payout: float, **kwargs) -> float: 
    # for theoretical_values(), machine_table()
    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    ts = kwargs['ts']

    ty = expected_loop * expected_rounds * payout
    out = ts * 250 / start
    
    return ty / out


# theoretical values and actual values

def theoretical_values(*args, **kwargs) -> pd.DataFrame:
    start, round_, payout, game = args
    rate = get_rate(start.mean(), payout.mean(), **kwargs)

    out = game.sum() * 250 / start.mean()
    bal = out * (rate - 1)
    # print(games, out, bal)

    df = pd.DataFrame(
        [[game.sum(), round(start.mean(), 2), round(payout.mean(), 2), round(rate, 2), round(bal, 1)]], 
        columns=['games', 'start', 'payout', 'rate', 'balance']
        )
    # print(df)
    return df


def actual_values(*args) -> pd.DataFrame:
    start, round_, payout, game = args
    out = game.sum() * 250 / start.mean()

    a_safe = round_ * payout
    safe = a_safe.sum()

    rate = safe / out
    bal = safe - out
    # print(out, safe, bal)

    df = pd.DataFrame(
        [[game.sum(), round(out), round(safe), round(rate, 2), round(bal, 1)]],
        columns=['games', 'out', 'safe', 'rate', 'balance']
    )
    # print(df)
    return df

# plot

def plot_data(*args):
    start, round_, payout, game = args

    out = game * ( 250 / start.mean())
    safe = round_ * payout
    balance = safe - out
    return game, balance


def plot(*args):
    games, balance = plot_data(*args)

    # fig = plt.figure() # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(games.cumsum(), balance.cumsum(), color='tab:cyan')
    ax.set_title('Chart', fontsize=16)
    # plt.show()
    canvas = FigureCanvasAgg(fig)
    img_io = io.BytesIO()
    canvas.print_png(img_io)
    png_output = img_io.getvalue()
    plot_img = base64.b64encode(png_output).decode('utf-8')

    return plot_img

# machine_table

def get_indices(df: pd.DataFrame) -> tuple[list, list]:
    p = re.compile('[0-9]+-[0-9]+')
    machine_indices =  [i for i, no in enumerate(df['machine-no']) if p.fullmatch(no)]
    end_of_indices = [idx - 2 for idx in machine_indices[1:]]
    end_of_indices.append(len(df['game-count']) - 1)

    return machine_indices, end_of_indices

def start_agg(df: pd.DataFrame) -> dict:
    machine_indices, end_of_indices = get_indices(df)
    d = {}
    for idx, end in zip(machine_indices, end_of_indices):
        machine_no = df['machine-no'][idx]
        sr = df['start'][idx:end]
        sr_droped = sr[sr != '']
        values = sr_droped.tolist()
        # 何かエラー処理
        if not machine_no in d.keys():
            d[machine_no] = values
        else:
            d[machine_no] += values
    # print(d)
    return d
        
def payout_agg(df: pd.DataFrame):
    machine_indices, end_of_indices = get_indices(df)
    d = {}
    for idx, end in zip(machine_indices, end_of_indices):
        machine_no = df['machine-no'][idx]
        payout = df['payout'][end]
        if isinstance(payout, (int, float)):
            if not machine_no in d.keys():
                d[machine_no] = [payout]
            else:
                d[machine_no] += [payout]
    # print(d)
    return d


def machine_table(df, **kwargs):
    start_d = start_agg(df)
    payout_d = payout_agg(df)
    l = []
    for key, val in start_d.items():
        start = (sum(val) / len(val)) if len(val) else float('nan')
        d = {
            'machine_no': key, 
            's_count': len(val), 
            'start': round(start, 2),
            'p_count': 0,
            'payout': float('nan'),
            'rate': float('nan')
        }
        if key in payout_d.keys():
            val_ = payout_d[key]
            payout = (sum(val_) / len(val_)) if len(val_) else float('nan')
            d['p_count'] = len(val_)
            d['payout'] = round(payout, 2)
            if not math.isnan(start) and not math.isnan(payout):
                rate = get_rate(start, payout, **kwargs)
                d['rate'] = round(rate, 2)

        l.append(d)
    df = pd.DataFrame(l)
    # print(df.sort_values(['start'], ascending=False))
    return df.sort_values(['start'], ascending=False)


if __name__ == "__main__":
    pass

