

def calc_rate(
    ts: float,             # TS：特賞スタート
    start: float,          # 千円スタート
    payout: float,         # 1ランドの払い出し
    expected_loop: float,  # 期待連荘数
    expected_rounds: float  # 期待ラウンド数
) -> float:
    ''' 台の割りを計算する '''
    ty = expected_loop * expected_rounds * payout
    out = ts * ( 250 / Start )
    return ty / out