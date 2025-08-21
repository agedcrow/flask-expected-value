import numpy as np
import pandas as pd


# PAスーパー海物語IN 沖縄5 SBA

def specs() -> dict:
    p = 1/99.9
    q = 1/9.9
    prize = {'heso': 3, 'dentu': 2, 'attacker': 11, 'ta_1': 3, 'ta_2': 4}
    count = 10
    round_ = 10, 5, 5
    ratio = 0.1, 0.57, 0.33  # ratio of probabilities
    st = 5
    jt = 95, 45, 20

    # 期待継続率、連荘数
    imb = 1 - (1-q)**5 * (1-p)**95  # imarine bounus - 10R
    odd = 1 - (1-q)**5 * (1-p)**45  # 6R
    even = 1 - (1-q)**5 * (1-p)**20  # 4R
    # continuing = np.dot((imb, odd, even), ratio)  # 0.6061
    # print(continuing)
    continuing = sum(a * b for a, b in zip((imb, odd, even), ratio))
    expected_loop = 1 / (1 - continuing)  # 2.5389

    # 期待ラウンド、払い出し、TY
    # expected_rounds = np.dot(round_, ratio)  # 5.5
    expected_rounds = sum(a * b for a, b in zip(round_, ratio))
    payout = prize['attacker'] * count - count  # 100
    ty = expected_loop * expected_rounds * payout # 1396.4

    # 実質TS
    x = 7 - 2  # 残保留7 - 欠損2
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


def specs_table(**d) -> pd.DataFrame:
    data = [
            [round(d['continuing'], 3)],
            [round(d['expected_loop'], 2)],
            [round(d['expected_rounds'], 1)],
            [round(d['payout'], 1)],
            [round(d['ty'], 1)],
            [round(d['border'], 2)],
            ['ヘソ 3 電チュ 2 左右下 4 左右上 3'],
            ['11 attack x 10 count x 5 or 10 R']
        ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', 'ボーダー', '賞球', 'カウント']

    return pd.DataFrame(data, index=index)


def border_table(**d):
    starts = np.arange(17, 24)
    payouts = np.arange(93, 103)

    expected_loop = d['expected_loop']
    expected_rounds = d['expected_rounds']
    arr_ty = expected_loop * expected_rounds * payouts

    ts = d['ts']
    arr_out = ts * 250 / starts

    data = [np.round(ty/arr_out, 3) for ty in arr_ty]
    df = pd.DataFrame(data, index=payouts, columns=starts)

    return df


if __name__ == '__main__':
    d = specs()
    print(d)
    # df = specs_table(**d)
    # print(df)
    # df = border_table(**d)
    # print(df)

