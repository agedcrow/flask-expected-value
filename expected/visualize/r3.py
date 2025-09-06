import numpy as np
import pandas as pd


# PA 海物語 3R3

def specs() -> dict:
    p = 1/99.9
    q = 1/16.9
    prize = {'heso': 3, 'dentu': 2, 'attacker': 10, 'ta_1': 1, 'ta_2': 4}
    count = 10
    round_ = 10, 5, 5
    ratio = 0.05, 0.46, 0.49  # ratio of probabilities
    jt = 40

    # 継続率、連荘数
    pull_back = 1 - (1-p)**jt  # 時短引戻し
    continuing = sum(a * b for a, b in zip((1, 1, pull_back), ratio))
    expected_loop = 1 / (1 - continuing)
    # ラウンド、払い出し、TY
    expected_rounds = sum(a * b for a, b in zip(round_, ratio))
    payout = prize['attacker'] * count - count  # 100
    ty = expected_loop * expected_rounds * payout # 1396.4

    # 実質TS
    x = 4 - 2  # 残保留 - 欠損
    ts = (1 - (1 - (1-p)**x)) * 1/p
    
    # ボーダー
    p_ = 1 / ts
    border = 250 / (ty * p_)

    d = {}
    d['p'] = p
    d['continuing'] = continuing
    d['expected_loop'] = expected_loop
    d['expected_rounds'] = expected_rounds
    d['payout'] = payout
    d['ty'] = ty
    d['ts'] = ts
    d['border'] = border

    return d


if __name__ == '__main__':
    d = specs()
    print(d)