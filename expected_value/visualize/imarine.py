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
    continuing = np.dot((imb, odd, even), ratio)  # 0.6061
    expected_loop = 1 / (1 - continuing)  # 2.5389

    # 期待ラウンド、払い出し、TY
    expected_rounds = np.dot(round_, ratio)  # 5.5
    payout = prize['attacker'] * count - count  # 100
    ty = expected_loop * expected_rounds * payout # 1396.4

    # 実質TS
    x = 7 - 2  # 残保留7 - 欠損2
    ts = (1 - (1 - (1-p)**x)) * 1/p
    
    # ボーダー
    p_ = 1 / ts
    border = 250 / (ty * p_)

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


def specs_table(**kwargs: np.float64) -> pd.DataFrame:
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
            ['ヘソ 3 電チュ 2 左右下 4 左右上 3'],
            ['11 attack x 10 count x 5 or 10 R']
        ]
    index = ['継続率', '期待連荘', '期待R', '出玉/R', 'TY', 'ボーダー', '賞球', 'カウント']

    return pd.DataFrame(data, index=index)


def border_table(**kwargs: np.float64):
    payouts = np.arange(93, 103)
    starts = np.arange(17, 24)
    expected_loop = kwargs['expected_loop']
    expected_rounds = kwargs['expected_rounds']
    ts = kwargs['ts']
    tys = expected_loop * expected_rounds * payouts

    out = ts * 250 / starts
    data = [np.round(ty/out, 3) for ty in tys]
    df = pd.DataFrame(data, index=payouts, columns=starts)

    return df


if __name__ == '__main__':
    d = spesc()
    print(d)
    df = specs_table(**d)
    print(df)
    df = border_table(**d)
    print(df)

