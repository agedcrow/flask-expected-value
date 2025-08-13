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

    return np.array(starts), np.array(rounds, dtype=int), np.array(payouts), np.array(games, dtype=int)


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


if __name__ == "__main__":
    pass

