


# 実質TS
def ts_utime(p: float, loss: float, utime_densup: int, games: float) -> float:
    '''遊タイム中に当たる確率を除いた初当たり確率が実質TS
    Args:
        p (float): 通常確率
        loss (float): 残保留の欠損
        utime_densup (int): 遊タイムのゲーム数
        games (float): 遊タイムまでのゲーム数 (平均ゲーム数を使うことがあるため float)
    Returns:
        ts (float): 実質の特賞スタート（確率分母）
    '''
    ts_ = (1 - (1 - (1-p)**loss)) * 1/p
    p_ = 1 / ts_
    hit_before_utime = 1 - (1-p_)**games
    reach_to_utime = 1 - hit_before_utime
    hit_in_utime = 1 - (1-p_)**utime_densup
    p_reach_and_hit = reach_to_utime * hit_in_utime
    ts = (1-p_reach_and_hit) * 1/p_

    return ts


if __name__ == '__main__':
    ts = ts_utime(p=1/99.9, loss=2.0, games=299-38.5, utime_games=379)
    print(ts)