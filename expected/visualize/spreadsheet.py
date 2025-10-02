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
from typing import Any
from expected.visualize.models import Sheet, Spec


''' google spreadsheet のデータを取得 '''

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'secrets', 'token.json')
SSKEY_FILE = os.path.join(os.path.dirname(__file__), 'secrets', 'sskey.json')


def get_spreadsheet_key(machine_name: str) -> str:
    d = {}
    with open(SSKEY_FILE, 'r') as f:
        d = json.load(f)
    try:
        spreadsheet_key = d[machine_name]
        return spreadsheet_key
    except KeyError as e:
        print(f'Key Error: {e}')
        return ''


def connect_gspread(SPREADSHEET_KEY: str) -> list:
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(TOKEN_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    
    return worksheets


def ws2df(worksheet: Any) -> pd.DataFrame:
    columns =  ['machine-no','count','out','start','loop','round','payout','game']
    
    df = pd.DataFrame(worksheet.get_all_records())
    print(df.columns.tolist())
    print(columns)
    if not df.columns.tolist()[:8] == columns:
        df = pd.DataFrame([['???'] + [float('nan')] * 7], columns=columns)
    print(df)
    return df


def get_spreadsheet_data(machine_name: str) -> pd.DataFrame:
    key = get_spreadsheet_key(machine_name)
    worksheets = connect_gspread(key)
    worksheet = worksheets[0]
    df = ws2df(worksheet)
    return df


''' 機械割の計算 '''

def get_rate(m_spec: Spec, start: float, payout: float, ts: float|None = None) -> float:
    expected_loop = m_spec.expected_loop
    expected_rounds = m_spec.expected_rounds
    ts = ts if ts else m_spec.ts

    ty = expected_loop * expected_rounds * payout
    out = ts * 250 / start
    
    return ty / out


''' 表とグラフの作成 '''

def to_numpy(sr: pd.Series) -> np.ndarray:
    if sr.name in ('machine-no', 'description'):
        a = sr.to_numpy()  # dtype: object
    else:
        a = pd.to_numeric(sr, errors='coerce').to_numpy()
    return a


def sheet_model(df: pd.DataFrame) -> Sheet:
    m = Sheet()
    m.machine_no = to_numpy(df['machine-no'])
    m.count = to_numpy(df['count'])
    m.out = to_numpy(df['out'])
    m.start = to_numpy(df['start'])
    m.round = to_numpy(df['round'])
    m.payout = to_numpy(df['payout'])
    m.game = to_numpy(df['game'])
    m.desc = to_numpy(df['description'])

    return m

def remove_nan(a):
    return a[~np.isnan(a)]

def calc_start(m: Sheet) -> tuple[float, float]:
    out = remove_nan(m.out)
    start = remove_nan(m.start)
    count = start * (out / 250)
    start_mean = count.sum() / (out.sum() / 250)

    game = remove_nan(m.game)
    out_sum = game.sum() * 250 / start_mean

    return start_mean, out_sum


def calc_payout(m: Sheet) -> float:
    round_ = remove_nan(m.round)
    payout = remove_nan(m.payout)
    safe = round_ * payout
    payout_mean = safe.sum() / round_.sum()

    return payout_mean


def expected_table(m: Sheet, m_spec: Spec) -> pd.DataFrame:
    game = remove_nan(m.game)
    start_mean, out_sum = calc_start(m)
    payout_mean = calc_payout(m)
    rate = get_rate(m_spec, start_mean, payout_mean)
    balance = out_sum * (rate - 1)

    df = pd.DataFrame(
        [[
            round(game.sum()), 
            round(start_mean, 2), 
            round(payout_mean, 2), 
            round(rate, 2), 
            round(balance, 1)
            ]], 
        columns=('game', 'start', 'payout', 'rate', 'balance')
        )

    return df

''' utime '''

from expected.visualize.utime import ts_utime

def get_start_games(m: Sheet):
    machine_no = m.machine_no
    count = m.count
    p = re.compile('[0-9]+-[0-9]+')
    idx = [i for i, n in enumerate(machine_no) if p.fullmatch(n)]
    
    return count[idx]

def expected_utime_table(m: Sheet, spec: Spec):
    game = remove_nan(m.game)
    start_mean, out_sum = calc_start(m)
    payout_mean = calc_payout(m)
    
    sg = get_start_games(m)
    games = spec.utime_timer - sg.mean()
    print(spec.p, spec.loss, spec.utime_densup, games)
    ts = ts_utime(spec.p, spec.loss, spec.utime_densup, games)
    rate = get_rate(spec, start_mean, payout_mean, ts=ts)
    balance = out_sum * (rate - 1)

    df = pd.DataFrame(
        [[
            round(game.sum()), 
            round(sg.mean()),
            round(start_mean, 2), 
            round(payout_mean, 2), 
            round(rate, 2), 
            round(balance, 1)
            ]], 
        columns=('game', 'sg', 'start', 'payout', 'rate', 'balance')
        )

    return df

def real_table(m: Sheet):
    game = remove_nan(m.game)
    start_mean, out_sum = calc_start(m)

    round_ = remove_nan(m.round)
    payout = remove_nan(m.payout)

    safe_sum = (round_ * payout).sum()
    rate = safe_sum / out_sum

    balance = safe_sum - out_sum

    df = pd.DataFrame(
        [[
            round(game.sum()), 
            round(out_sum), 
            round(safe_sum), 
            round(rate, 2), 
            round(balance, 1)]],
        columns=['game', 'out', 'safe', 'rate', 'balance']
    )
    return df

# plot

def _plot_data(m: Sheet):
    start_mean, _ = calc_start(m)
    payout_mean = calc_payout(m)

    a1 = m.game
    a2 = m.round
    game = a1[~np.isnan(a1)]
    round_ = a2[~np.isnan(a2)]

    out = game * ( 250 / start_mean)
    safe = round_ * payout_mean
    balance = safe - out
    return game, balance


def plot(m: Sheet):
    game, balance = _plot_data(m)

    # fig = plt.figure() # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(game.cumsum(), balance.cumsum(), color='tab:cyan')
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


''' 機械番号別の情報 '''

def machine_indexes(m: Sheet) -> list:
    machine_no = m.machine_no
    count = m.count

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

def start_of_machine(m: Sheet, m_idx: list) -> dict[str, list]:
    machine_no = m.machine_no
    out_nan = m.out
    start_nan = m.start
    # d: dict[str, list] = {}
    d = {}
    for idx, btm in m_idx:
        n = machine_no[idx]
        start = remove_nan(start_nan[idx:btm])
        if start.size:
            out = remove_nan(out_nan[idx:btm])
            count = start * (out / 250)

            val = [int(count.sum()), int(out.sum())]
            if not n in d.keys():
                d[n] = val
            else:
                d[n][0] += val[0]
                d[n][1] += val[1]

    return d


def payout_of_machine(m: Sheet, m_idx: list) -> dict[str, list]:
    machine_no = m.machine_no
    round_ = m.round
    payout = m.payout
    d = {}
    for idx, btm in m_idx:
        m_no = machine_no[idx]

        m_round = remove_nan(round_[idx:btm])
        m_payout = remove_nan(payout[idx:btm])

        if m_round.size == m_payout.size == 1:
            rnd = m_round[0]
            pay = m_payout[0]

            val = [int(rnd), int(rnd * pay)]
            if not m_no in d.keys():
                d[m_no] = val
            else:
                d[m_no][0] += val[0]
                d[m_no][1] += val[1]

    return d


def desc_of_machine(m: Sheet, m_idx: list) -> dict[str, str]:
    machine_no = m.machine_no
    desc = m.desc
    d = {}
    for idx, _ in m_idx:
        m_no = machine_no[idx]
        m_desc = desc[idx]
        d[m_no] = m_desc if m_desc else ''

    return d


def machine_table(m: Sheet, spec: Spec):
    idx = machine_indexes(m)
    start_d = start_of_machine(m, idx)
    payout_d = payout_of_machine(m, idx)
    desc_d = desc_of_machine(m, idx)
    data = []
    for key, val in start_d.items():
        count, out = val
        print(val)
        start = count / (out / 250)
        desc = desc_d[key] if key in desc_d.keys() else ''
        d = {
            'machine': key, 
            'count': count,
            'start': round(start, 2),
            'payout': float('nan'),
            'rate': float('nan'),
            'desc': desc
        }
        if key in payout_d.keys():
            round_sum, payout_sum = payout_d[key]
            payout = payout_sum / round_sum
            d['payout'] = round(payout, 2)
            if not math.isnan(start) and not math.isnan(payout):
                # get_rate()
                rate = get_rate(spec, start, payout)
                d['rate'] = round(rate, 2)

        data.append(d)
    df_ = pd.DataFrame(data)
    return df_.sort_values(['start'], ascending=False)


if __name__ == "__main__":

    # from expected.visualize import imarine
    # m_spec = imarine.imarine_spec()

    from expected.visualize import agnes4
    m_spec = agnes4.agnes4_spec()

    machine_name = 'agnes4'
    df = get_spreadsheet_data(machine_name)
    m_sheet = sheet_model(df)
    # df = expected_table(m_sheet, m_spec)
    # print(df)
    # df = real_table(m_sheet)
    # print(df)
    # df = machine_table(m_sheet, m_spec)
    # print(df)
    df = expected_func(m_sheet, m_spec)
    print(df)
