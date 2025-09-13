import numpy as np
import pandas as pd

import base64
import io
import json
import os
from expected.visualize.models import Spec
from typing import Any


# PA大海物語4スペシャル RBA

# 実質TS
def ts_utime(p: float, loss: float, utime_densup: int, games: float) -> float:
    ts_ = (1 - (1 - (1-p)**loss)) * 1/p
    p_ = 1 / ts_
    hit_before_utime = 1 - (1-p_)**games
    reach_to_utime = 1 - hit_before_utime
    hit_in_utime = 1 - (1-p_)**utime_densup
    p_reach_and_hit = reach_to_utime * hit_in_utime
    ts = (1-p_reach_and_hit) * 1/p_

    return ts

def agnes4_spec() -> Spec:
    p = 1/99.9
    q = 1/19.5
    prize = {'heso': 3, 'dentu': 2, 'attacker': 12, 'ta_1': 2, 'ta_2': 4}
    count = 9
    round_ = 10, 6, 4, 4
    ratio = 0.04, 0.6, 0.06, 0.3
    st = 10
    jt = 90, 40, 40, 15
    utime_timer = 299
    utime_densup = 379

    agnes = 1 - (1-q)**10 * (1-p)**90
    odd   = 1 - (1-q)**10 * (1-p)**40
    even1 = 1 - (1-q)**10 * (1-p)**40
    even2 = 1 - (1-q)**10 * (1-p)**15
    continuing = sum(a * b for a, b in zip((agnes, odd, even1, even2), ratio))
    expected_loop = 1 / (1 - continuing)

    expected_rounds = sum(a * b for a, b in zip(round_, ratio))
    payout = prize['attacker'] * count - count
    ty = expected_loop * expected_rounds * payout

    ds = map(lambda x: x+10+4, jt)  # 電サポ（ST + 時短 + 残保留）
    start_game = sum(a * b for a, b in zip(ds, ratio))  # 48.5
    loss = -2  # 欠損 4 - 6
    games = utime_timer - start_game
    ts = ts_utime(p=p, loss=loss, utime_densup=utime_densup, games=games)
    # ボーダー
    p_ = 1 / ts
    border = 250 / (ty * p_)

    m = Spec()
    m.p = p
    m.continuing = continuing
    m.expected_loop = expected_loop
    m.expected_rounds = expected_rounds
    m.payout = payout
    m.ty = ty
    m.ts = ts
    m.border = border
    m.loss = loss
    m.utime_timer = utime_timer
    m.utime_densup = utime_densup

    return m

def spec_table(m: Spec) -> pd.DataFrame:
    data = [
            [round(m.continuing, 3)],
            [round(m.expected_loop, 2)],
            [round(m.expected_rounds, 1)],
            [round(m.payout, 1)],
            [round(m.ty, 1)],
            [round(m.border, 2)],
            ['ヘソ 3 電チュ 2 左上・右上 2 他 4'],
            ['12 attack x 9 count x 4 or 6 or 10R']
    ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', 'ボーダー(48.5G)', '賞球', 'カウント']
    return pd.DataFrame(data, index=index)


def border_tables(m: Spec, *start_games: int) -> pd.DataFrame:
    payouts = np.array([95, 96, 97, 98, 99, 100, 101])
    starts = np.arange(15, 23)
    expected_loop = m.expected_loop
    expected_rounds = m.expected_rounds
    # ts = m.ts

    ts_list = []
    for g in start_games:
        games = m.utime_timer - g
        ts = ts_utime(m.p, m.loss, m.utime_densup, games)
        ts_list.append(ts)

    dfs = []
    for ts in ts_list:
        out = ts * 250 / starts
        ty = expected_loop * expected_rounds * payouts
        
        data = [np.round(t/out, 3) for t in ty]
        df = pd.DataFrame(data, index=payouts, columns=starts)
        dfs.append(df)

    return dfs


if __name__ == '__main__':
    # res = ts_utime(p=1/99.9, loss=-2, games=299-133, utime_games=379)
    # print(res)
    m = agnes4_spec()
    # print(type(m))
    df = spec_table(m)
    print(df)
    sg = 34, 54, 80, 110, 140, 170
    # dfs = border_tables(m, *sg)
    # print(dfs[-1])
