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


def get_ws(spreadsheet_key):
    worksheets = connect_gspread(spreadsheet_key)
    ws = worksheets[0]
    
    return ws


def get_all_records(worksheet: object) -> pd.DataFrame:
    columns =  ['machine-no','count','out','start','loop','round','payout','game']
    
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.columns.tolist()[:8] == columns:
        df = pd.DataFrame([['???'] + [float('nan')] * 7], columns=columns)

    return df


def get_rate(start, payout, **kwargs) -> float: 
    """
    Lorem ipsum
    Args:
      start: float
      payout: float
    Keyword Args:
      key1: (int)

    """
    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    ts = kwargs['ts']

    ty = expected_loop * expected_rounds * payout
    out = ts * 250 / start
    
    return ty / out

def _start_aggregate(df: pd.DataFrame) -> tuple[float, float]:
    sr = df['out']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    out = sr_numeric.dropna().to_numpy()

    sr = df['start']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    start = sr_numeric.dropna().to_numpy()

    sr = df['game']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    games = sr_numeric.dropna().to_numpy()

    start_mean = float('nan')
    if out.size == start.size:
        count = start * (out / 250)
        start_mean = count.sum() / (out.sum() / 250)

    return start_mean, games

def _payout_aggregate(df: pd.DataFrame) -> tuple[float, float]:
    sr = df['round']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    rounds = sr_numeric.dropna().astype(int).to_numpy()

    sr = df['payout']
    sr_numeric = pd.to_numeric(sr, errors="coerce")
    payouts = sr_numeric.dropna().to_numpy()

    payout_mean = float('nan')
    if rounds.size == payouts.size:
        safe = rounds * payouts
        payout_mean = safe.sum() / rounds.sum()

    return payout_mean, rounds


def _aggregate(df: pd.DataFrame) -> tuple[float, float, np.ndarray, np.ndarray]:
    start_mean, games = _start_aggregate(df)
    payout_mean, rounds = _payout_aggregate(df)
    
    return start_mean, payout_mean, games, rounds


def theoretical_value(start_mean, payout_mean, games, **kwargs):

    rate = get_rate(start_mean, payout_mean, **kwargs)
    out = games.sum() * 250 / start_mean
    balance = out * (rate - 1)

    df = pd.DataFrame(
        [[
            round(games.sum()), 
            round(start_mean, 2), 
            round(payout_mean, 2), 
            round(rate, 2), 
            round(balance, 1)
            ]], 
        columns=('games', 'start', 'payout', 'rate', 'balance')
        )

    return df


def actual_value(start_mean, payout_mean, games, rounds):

    out = games.sum() * 250 / start_mean
    safe = rounds.sum() * payout_mean
    rate = safe / out
    balance = safe - out

    df = pd.DataFrame(
        [[
            round(games.sum()), 
            round(out), 
            round(safe), 
            round(rate, 2), 
            round(balance, 1)]],
        columns=['games', 'out', 'safe', 'rate', 'balance']
    )
    return df


def tables(start_mean, payout_mean, games, rounds, **specs):
    # ag = _aggregate(df)
    theoretical_table = theoretical_value(start_mean, payout_mean, games, **specs)
    actual_talbe = actual_value(start_mean, payout_mean, games, rounds)
    
    return theoretical_table, actual_talbe

# plot

def _plot_data(start_mean, payout_mean, games, rounds):
    out = games * ( 250 / start_mean)
    safe = rounds * payout_mean
    balance = safe - out
    return games, balance


def plot(start_mean, payout_mean, games, rounds):
    games, balance = _plot_data(start_mean, payout_mean, games, rounds)

    # fig = plt.figure() # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(games.cumsum(), balance.cumsum(), color='tab:cyan')
    ax.set_title('Chart', fontsize=16)
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    png_output = buf.getvalue()
    plot_img = base64.b64encode(png_output).decode('utf-8')

    # from PIL import Image
    # buf.seek(0)
    # img = Image.open(buf)
    # img.show()
    
    return plot_img


# machine_table

def cutout(df: pd.DataFrame):
    d = {
        'machine_no': df['machine-no'],
        'count': df['count'],
        'out': df['out'],
        'start': df['start'],
        'round': df['round'],
        'payout': df['payout'],
        'comment': df['comment']
    }
    return d


def machine_indexes(**kwargs) -> list:
    machine_no = kwargs['machine_no']
    count = kwargs['count']

    p = re.compile('[0-9]+-[0-9]+')
    indexes = []
    for idx, no in enumerate(machine_no):
        if p.fullmatch(no):
            indexes.append(idx)

    bottoms = []
    for idx in indexes[1:]:
        bottom = idx - 1
        bottoms.append(bottom)
    bottoms += [count.size - 1]

    return list(zip(indexes, bottoms))

def start_agg(indexes, **kwargs) -> dict:
    sr_machine_no = kwargs['machine_no']
    sr_out = kwargs['out']
    sr_start = kwargs['start']
    d = {}
    for idx, btm in indexes:
        machine_no = sr_machine_no[idx]
        
        s_out = sr_out[idx:btm]
        numeric = pd.to_numeric(s_out, errors="coerce")
        out = numeric.dropna().to_numpy()

        s_start = sr_start[idx:btm]
        numeric = pd.to_numeric(s_start, errors="coerce")
        start = numeric.dropna().to_numpy()
        
        game_count = start * (out / 250)

        val = [int(game_count.sum()), int(out.sum())]
        if not machine_no in d.keys():
            d[machine_no] = val
        else:
            d[machine_no][0] += val[0]
            d[machine_no][1] += val[1]
    # print(d)
    return d


def payout_agg(indexes, **kwargs):
    sr_machine_no = kwargs['machine_no']
    sr_round = kwargs['round']
    sr_payout = kwargs['payout']
    d = {}
    for idx, btm in indexes:
        machine_no = sr_machine_no[idx]

        s_round = sr_round[idx:btm]
        numeric = pd.to_numeric(s_round, errors="coerce")
        a_round = numeric.dropna().astype(int)

        if a_round.size == 1:
            round_ = a_round.values[0]

            s_payout = sr_payout[idx:btm]
            numeric = pd.to_numeric(s_payout, errors="coerce")
            payout = numeric.dropna().values[0]

            val = [int(round_), int(round_ * payout)]
            if not machine_no in d.keys():
                d[machine_no] = val
            else:
                d[machine_no][0] += val[0]
                d[machine_no][1] += val[1]

    return d


def comment_agg(indexes, **kwargs):
    sr_machine_no = kwargs['machine_no']
    sr_comment = kwargs['comment']
    d = {}
    for idx, _ in indexes:
        machine_no = sr_machine_no[idx]
        comment = sr_comment[idx]
        if not comment == '':
            d[machine_no] = comment

    return d


def machine_table(df, **kwargs):
    d = cutout(df)
    idx = machine_indexes(**d)
    start_d = start_agg(idx, **d)
    payout_d = payout_agg(idx, **d)
    comment_d = comment_agg(idx, **d)
    data = []
    for key, val in start_d.items():
        count, out = val
        start = count / (out / 250)
        comment = comment_d[key]
        d = {
            'machine_no': key, 
            'games': count, 
            'start': round(start, 2),
            'payout': float('nan'),
            'rate': float('nan'),
            'comment': comment
        }
        if key in payout_d.keys():
            round_sum, payout_sum = payout_d[key]
            payout = payout_sum / round_sum
            d['payout'] = round(payout, 2)
            if not math.isnan(start) and not math.isnan(payout):
                rate = get_rate(start, payout, **kwargs)
                d['rate'] = round(rate, 2)


        data.append(d)
    df_ = pd.DataFrame(data)
    return df_.sort_values(['start'], ascending=False)


if __name__ == "__main__":
    print(TOKEN_FILE, SSKEY_FILE)
    # key = get_sskey('imarine')
    # ws = get_ws(key)
    # df = get_all_records(ws)

    # # x = machine_indexes(df)
    # # print(x)
    # # d = start_agg(df)
    # # print(d)
    # # d = payout_agg(df)
    # # print(d)

    # from expected_value.visualize import imarine

    # spec = imarine.specs()
    # # print(spec)
    # df_ = machine_table(df, **spec)
    # print(df_)
