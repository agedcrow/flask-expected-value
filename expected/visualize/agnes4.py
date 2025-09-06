import numpy as np
import pandas as pd

import base64
import io
import json
import os


# PA大海物語4スペシャル RBA

# 実質TS
def actual_ts(games=299, utime_games=379):
    p = 1/99.9
    # 残保留 6 - 4
    x = -2  # 欠損2
    ts = (1 - (1 - (1-p)**x)) * 1/p
    p_ = 1 / ts
    # 遊タイム
    p_hit_before_utime = 1 - (1-p_)**games
    p_reach_to_utime = 1 - p_hit_before_utime
    p_hit_in_utime = 1 - (1-p_)**utime_games
    p_reach_and_hit_in_utime = p_reach_to_utime * p_hit_in_utime
    ts_actual = (1-p_reach_and_hit_in_utime) * 1/p_

    return ts_actual

def specs():
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

    expected_rounds = np.dot(round_, ratio)  # 期待ラウンド数 5.439
    payout = prize['attacker'] * count - count  # 表記出玉 99
    ty = expected_loop * expected_rounds * payout # 1274.25

    # 実質TS
    ts = actual_ts()
    # ボーダー
    actual_p = 1 / ts
    border = 250 / (ty * actual_p)

    d = {
            'continuing': continuing,  # 継続率
            'expected_loop': expected_loop,  # 期待連荘数
            'expected_rounds': expected_rounds,  # 期待ラウンド数
            'payout': payout,  # 1ラウンドの払い出し
            'ty': ty,  # 特賞の（寄り玉）期待出玉
            'ts': np.float64(ts),  # 実質の（特賞スタート）通常確率分母
            'border': border  # ボーダー
        }

    return d

def specs_table(**kwargs):
    continuing = kwargs['continuing']
    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    payout = kwargs['payout']
    ty = kwargs['ty']
    border = kwargs['border']
    data = [
            [round(continuing, 3)],
            [round(expected_loop, 2)],
            [round(expected_rounds, 1)],
            [round(payout, 1)],
            [round(ty, 1)],
            [round(border, 2)],
        ['ヘソ 3 電チュ 2 左上・右上 2 他 4'],
        ['12 attack x 9 count x 4 or 6 or 10R']
    ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', 'ボーダー', '賞球', 'カウント']
    return pd.DataFrame(data, index=index)


def border_tables(*args: int, **kwargs: np.float64) -> pd.DataFrame:
    payouts = np.array([95, 96, 97, 98, 99, 100, 101])
    starts = np.arange(15, 23)
    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    ts = kwargs['ts']

    dfs = []
    for ts in [actual_ts(games=(299-game)) for game in args]:
        out = ts * 250 / starts
        tys = expected_loop * expected_rounds * payouts
        
        data = [np.round(ty/out, 3) for ty in tys]
        df = pd.DataFrame(data, index=payouts, columns=starts)
        dfs.append(df)

    return dfs


if __name__ == '__main__':
    d = specs()
    # print(d)
    # df = specs_table(**d)
    # print(df)
    args = 0, 33, 53, 90, 120, 160, 190
    dfs = border_tables(*args, **d)
    print(dfs[-1])
