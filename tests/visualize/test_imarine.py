from pathlib import Path
import pandas as pd
import pytest


@pytest.fixture
def sheet():
    path = Path(__file__).parent.joinpath('imarine.csv')
    return pd.read_csv(path)


def test_spam(sheet):
    print('\n', sheet)
    assert 1