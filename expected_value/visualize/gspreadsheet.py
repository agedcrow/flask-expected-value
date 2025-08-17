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

from .models import Result
from flask import current_app

TOKEN_FILE = os.path.join(current_app.instance_path, 'token.json')
SSKEY_FILE = os.path.join(current_app.instance_path, 'sskey.json')


def spreadsheet_keys() -> dict:
    d = {}
    with open(SSKEY_FILE, 'r') as f:
        d = json.load(f)
    return d

def connect_gspread(SPREADSHEET_KEY: str) -> list:

    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(TOKEN_FILE, scopes=scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = workbook.worksheets()
    
    return worksheets




def arrays_from_sheet(machine_name: str):

    d = spreadsheet_keys()
    spreadsheet_key = d[machine_name]
    worksheets = connect_gspread(spreadsheet_key)
    ws = worksheets[0]

    col_starts = ws.col_values(3)  # 回転数
    col_rounds = ws.col_values(5)  # トータルラウンド数
    col_payouts = ws.col_values(6)  # 払出/R
    col_games = ws.col_values(7)  # （通常）ゲーム数

    def is_num(s):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True

    starts = [float(s) for s in col_starts if is_num(s)]

    rounds, payouts, games = [], [], []
    for r, p, g in zip(col_rounds, col_payouts, col_games):
        if all([is_num(r), is_num(p), is_num(g)]):
            rounds.append(int(r))
            payouts.append(float(p))
            games.append(int(g))

    m = Result()
    m.starts = starts
    m.rounds = rounds
    m.payouts = payouts
    m.games = games

    return np.array(starts), np.array(rounds, dtype=int), np.array(payouts), np.array(games, dtype=int)


def theoretical_value(starts, payouts, **kw):
    ...

def result(
        starts: np.ndarray,
        rounds: np.ndarray,
        payouts: np.ndarray,
        games: np.ndarray,
        **kwargs: np.float64
    ) -> pd.DataFrame:
    mean_start = starts.mean()
    mean_payout = (rounds * payouts).sum() / rounds.sum()
    out = (250 * games / mean_start).sum()
    saf = (rounds * payouts).sum()
    rate = saf / out

    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    ts = kwargs['ts']

    ty = expected_loop * expected_rounds * mean_payout
    mean_out = ts * 250 / mean_start
    expected_rate = ty/mean_out

    data = [[
            round(mean_start, 2), 
            round(mean_payout, 2),
            round(expected_rate, 2),
            round(out), 
            round(saf),
            round(saf) - round(out),
            round(rate, 2)
        ]]
    columns = ['Start', 'Payout', 'Exp', 'OUT', 'SAF', 'Bal', 'Rate']
    df = pd.DataFrame(data, columns=columns)

    return df


def plot_data(
        starts: np.ndarray,
        rounds: np.ndarray,
        payouts: np.ndarray,
        games: np.ndarray
    ):
    balance = rounds * payouts - 250 * games / starts.mean()
    return games, balance


def plot(games: np.ndarray, balance: np.ndarray):

    # fig = plt.figure() # UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(games.cumsum(), balance.cumsum(), color='tab:cyan')
    ax.set_title(f'Games: {int(games.sum())}', fontsize=16)
    # plt.show()
    canvas = FigureCanvasAgg(fig)
    img_io = io.BytesIO()
    canvas.print_png(img_io)
    png_output = img_io.getvalue()
    plot_img = base64.b64encode(png_output).decode('utf-8')

    return plot_img


# new world

def get_sskey(machine_name: str) -> str:
    d = spreadsheet_keys()
    spreadsheet_key = d[machine_name]
    return spreadsheet_key

def get_all_records(key: str, col_count=7) -> pd.DataFrame:
    worksheets = connect_gspread(key)
    ws = worksheets[0]
    df = pd.DataFrame(ws.get_all_records())
    # if not len(df['game-count']) == len(df):
    #     pass
    # if not col_count < df.columns.size:
    #     pass
    return df


def df2dict(df: pd.DataFrame) -> dict:
    pt = re.compile('[0-9]+-[0-9]+')
    indexes = [idx for idx, no in enumerate(df['machine-no']) if pt.fullmatch(no)]
    bottom_rows = [idx - 2 for idx in indexes[1:]]
    row_count = len(df['game-count'])
    bottom_rows.append(row_count - 1)
    d = {}
    for i, (idx, btm) in enumerate(zip(indexes, bottom_rows)):
        machine_no = df['machine-no'][idx]
        sr = df['starts'][idx:btm]
        sr_droped = sr[sr != '']
        values = sr_droped.tolist()
        # 何かエラー処理
        if not machine_no in d.keys():
            d[machine_no] = values
        else:
            d[machine_no] += values
    # print(d)
    return d
        

def stat_for_starts(d: dict):
    l = []
    for key in d.keys():
        val = d[key]
        l.append({
            'machine_no': key, 
            'count': len(val), 
            'mean': round(sum(val) / (len(val) if len(val) else 1), 1), 
            's': ' '.join([str(x) for x in val])
        })

    sorted_l = sorted(l, key=lambda x: x['mean'], reverse=True)
    # print(sorted_l)
    return sorted_l


if __name__ == "__main__":
    pass

