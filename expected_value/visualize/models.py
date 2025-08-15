from pydantic import BaseModel, Field
# from typing import Annotated, Optional
import numpy as np


class Specs(BaseModel):
    p : float = Field(default=float('nan'))
    continuing: float = Field(default=float('nan'))  # 継続率
    expected_loop: float = Field(default=float('nan'))   # 特賞に対する期待連荘数
    expected_rounds: float = Field(default=float('nan')) # 1回の当たりに対する期待ラウンド数
    payout: float = Field(default=float('nan'))      # 1ラウンドの払い出し
    ty: float = Field(default=float('nan'))          # 特賞の（寄り玉）期待出玉
    ts: float = Field(default=float('nan'))          # 実質の特賞スタート
    border: float = Field(default=float('nan'))      # ボーダー

