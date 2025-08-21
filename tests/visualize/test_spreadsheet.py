import numpy as np
import pytest


@pytest.fixture
def ss(app):
    with app.app_context():
        from expected_value.visualize import spreadsheet
        return spreadsheet

KEY = 'test_seastory'

def test_spreadsheet_keys(ss):
    d = gss.spreadsheet_keys()
    assert KEY in d.keys()


def test_connect_gspread(ss):
    expected = [['machine-no']]

    d = gss.spreadsheet_keys()
    spreadsheet_key = d[KEY]

    worksheets = gss.connect_gspread(spreadsheet_key)
    ws = worksheets[0]
    assert expected == ws.get('A1')


def test_arrays_from_sheet(ss):
    starts, rounds, payouts, games = gss.arrays_from_sheet(KEY)
    assert 63 == np.floor(starts).sum()
    assert 25 == rounds.sum()
    assert 194 == np.floor(payouts).sum()
    assert 279 == games.sum()
