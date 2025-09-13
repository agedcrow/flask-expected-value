import numpy as np
from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated


def to_numpy(a):
    if isinstance(a, list):
        return np.array(a)
    if isinstance(a, np.ndarray):
        return a
    raise TypeError('array must be list or numpy.ndarray')

NdArray = Annotated[np.ndarray, BeforeValidator(to_numpy)]


class Spec(BaseModel):
    p: float = Field(default=float('nan'))
    continuing: float = Field(default=float('nan'))
    expected_loop: float = Field(default=float('nan'))
    expected_rounds: float = Field(default=float('nan'))
    payout: float = Field(default=float('nan'))
    ty: float = Field(default=float('nan'))
    ts: float = Field(default=float('nan'))
    border: float = Field(default=float('nan'))
    loss: float = Field(default=float('nan'))
    utime_timer: int = Field(default=0)
    utime_densup: int = Field(default=0)


class Sheet(BaseModel):
    machine_no: NdArray = Field(default=None)
    count: NdArray = Field(default=None)
    out: NdArray = Field(default=None)
    start: NdArray = Field(default=None)
    round: NdArray = Field(default=None)
    payout: NdArray = Field(default=None)
    game: NdArray = Field(default=None)
    desc: NdArray = Field(default=None)

    model_config = {
        'arbitrary_types_allowed': True  
        # pydantic.errors.PydanticSchemaGenerationErrorの解消
    }

    # @classmethod
    # def from_mongo(cls, d: dict):
    #     d['_id'] = str(d['_id'])
    #     return cls(**d)

    # def to_mongo(self) -> dict:
    #     d = self.model_dump()
    #     if 'id' in d.keys():
    #         d["_id"] = ObjectId(d.pop('id'))
    #     return d

if __name__ == '__main__':
    # m = Spec()
    # m.p = 0.99
    m = Sheet()
    print(m)