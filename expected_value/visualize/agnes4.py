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

# PA大海物語4スペシャル RBA

def border():
    p = 1/99.9
    q = 1/19.5
    prize = {'heso': 3, 'dentu': 2, 'attacker': 12, 'ta_1': 2, 'ta_2': 4}
    count = 9
    round_ = 10, 6, 4, 4
    ratio = 0.04, 0.6, 0.06, 0.3
    st = 10
    jt = 90, 40, 40, 15

    agnes = 1 - (1-q)**10 * (1-p)**90
    odd   = 1 - (1-q)**10 * (1-p)**40
    even1 = 1 - (1-q)**10 * (1-p)**40
    even2 = 1 - (1-q)**10 * (1-p)**15
    continuing = np.dot((agnes, odd, even1, even2), ratio)  # 継続率 0.5773
    expected_loop = 1 / (1 - continuing)  # 期待連荘数 2.3660
    # print(continuing, expected_loop)

    expected_rounds = np.dot(round_, ratio)  # 期待ラウンド数 5.439
    payout = prize['attacker'] * count - count  # 表記出玉 99
    ty = expected_loop * expected_rounds * payout # 1274.25
    # print(expected_rounds, payout, ty)

    # 実質TS
    def expected_ts(games=299, utime_games=379):
        p_hit_before_utime = 1 - (1-p)**games
        p_reach_to_utime = 1 - p_hit_before_utime
        p_hit_in_utime = 1 - (1-p)**utime_games
        p_reach_and_hit_in_utime = p_reach_to_utime * p_hit_in_utime
        ts = (1-p_reach_and_hit_in_utime) * 1/p
        return ts

    ts = expected_ts()  # default value
    p_ = 1 / ts
    border = 250 / (ty * p_)
    # print(ts, border)  # 95.0752221500156 18.65312045778898

    # tables
    start_games = [0, 30, 50, 80, 100, 130, 160, 190]
    dfs = []
    for ts in [expected_ts(games=(299-g)) for g in start_games]:
        payouts = np.array([95, 96, 97, 98, 99, 100, 101])
        starts = np.arange(15, 23)
        out = ts * 250 / starts
        arr_ty = expected_loop * expected_rounds * payouts
        
        data = [np.round(ty/out, 3) for ty in arr_ty]
        df = pd.DataFrame(data, index=payouts, columns=starts)
        dfs.append(df)

    return dfs, start_games


def spec():
    data = [
        [0.5773],
        [2.366],
        [5.439],
        [99],
        [1274.2],
        ['ヘソ 3 電チュ 2 左上・右上 2 他 4'],
        ['12 attack x 9 count x 4 or 6 or 10R']
    ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', '賞球', 'カウント']
    return pd.DataFrame(data, index=index)


if __name__ == '__main__':
    dfs, start_games = border()
    print(dfs[-1])