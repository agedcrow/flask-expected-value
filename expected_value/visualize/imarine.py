import numpy as np
import pandas as pd

import base64
import io
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from expected_value.visualize.gspreadsheet import connect_gspread, get_sskey

# PAスーパー海物語IN 沖縄5 SBA

def border():
    p = 1/99.9
    q = 1/9.9
    prize = {'heso': 3, 'dentu': 2, 'attacker': 11, 'ta_1': 3, 'ta_2': 4}
    count = 10
    round_ = 10, 5, 5
    ratio = 0.1, 0.57, 0.33
    st = 5
    jt = 95, 45, 20

    # 期待継続数
    imb = 1 - (1-q)**5 * (1-p)**95  # imarine bounus 10R
    odd = 1 - (1-q)**5 * (1-p)**45
    even = 1 - (1-q)**5 * (1-p)**20
    continuing = np.dot((imb, odd, even), ratio)  # 合算継続率 0.6061
    expected_loop = 1 / (1 - continuing)  # 期待連荘数 2.5389

    # TY
    expected_rounds = np.dot(round_, ratio)  # 期待ラウンド数 5.5
    payout = prize['attacker'] * count - count  # 表記出玉 -> 100
    ty = expected_loop * expected_rounds * payout # 1396.4
    # print(continuing, expected_loop, expected_rounds, payout, ty)

    # 実質TS
    z = 8 - 2  # 残保留 z 欠損2
    ts = (1 - (1 - (1-p)**z)) * 99.9
    p_ = 1 / ts
    border_ = 250 / (ty * p_)
    # -> TS:94.0 TY:1396.4 Border:16.8

    payouts = np.arange(93, 103)
    starts = np.arange(17, 24)
    ty_arr = expected_loop * expected_rounds * payouts
    out = ts * 250 / starts

    data = [np.round(ty/out, 3) for ty in ty_arr]
    df = pd.DataFrame(data, index=payouts, columns=starts)

    return df


def spec():
    data = [
            [0.6061],
            [2.539],
            [5.5],
            [100],
            [1396.4],
            ['ヘソ 3 電チュ 2 左右下 4 左右上 3'],
            ['11 attack x 10 count x 5 or 10 R']
        ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', '賞球', 'カウント']
    return pd.DataFrame(data, index=index)


def result():

    def is_num(s):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True
    
    d = get_sskey()
    spreadsheet_key = d['imarine']
    worksheets = connect_gspread(spreadsheet_key)
    ws = worksheets[0]

    col_starts = ws.col_values(3)  # 回転数
    col_rounds = ws.col_values(5)  # トータルラウンド数
    col_payouts = ws.col_values(6)  # 払出/R
    col_games = ws.col_values(7)  # （通常）ゲーム数

    tmp = []
    for t in zip(col_rounds, col_payouts, col_games):
        if all([is_num(x) for x in t]):
            tmp.append([float(x) for x in t])

    arr = np.array(tmp)
    rounds, payouts, games = arr[:, 0], arr[:, 1], arr[:, 2]
    starts = [float(s) for s in col_starts if is_num(s)]

    mean_start = np.array(starts).mean()
    mean_payout = (rounds * payouts).sum() / rounds.sum()
    out = (250 * games / mean_start).sum()
    saf = (rounds * payouts).sum()
    rate = saf / out

    # expected rate
    expected_loop = 2.539
    expected_rounds = 5.5
    ts = 94.0
    ty_ = expected_loop * expected_rounds * mean_payout
    out_ = 250 * ts / mean_start
    expected_rate = ty_ / out_

    # for plot
    balance = rounds * payouts - 250 * games / mean_start

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

    return df, games, balance


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
    img_data = base64.b64encode(png_output).decode('utf-8')

    return img_data

if __name__ == '__main__':
    pass

    # df, games, balance = result()
    # print(df)

    # d = get_sskey()
    # SPREADSHEET_KEY = d['imarine'] 
    # worksheets = connect_gspread(SPREADSHEET_KEY)
    # ws = worksheets[0]
    # print(ws.cell(1, 1).value)

    # df_border = border()
    # print(df_border)

    # df_spec = spec()
    # print(df_spec)

