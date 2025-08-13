import numpy as np
import pytest


@pytest.fixture
def gss(app):
    with app.app_context():
        from expected_value.visualize import gspreadsheet
        return gspreadsheet

KEY = 'test_seastory'

def test_spreadsheet_keys(gss):
    d = gss.spreadsheet_keys()
    assert KEY in d.keys()


def test_connect_gspread(gss):
    expected = [['machine-no']]

    d = gss.spreadsheet_keys()
    spreadsheet_key = d[KEY]

    worksheets = gss.connect_gspread(spreadsheet_key)
    ws = worksheets[0]
    assert expected == ws.get('A1')


def test_arrays_from_sheet(gss):
    starts, rounds, payouts, games = gss.arrays_from_sheet(KEY)
    assert 63 == np.floor(starts).sum()
    assert 25 == rounds.sum()
    assert 194 == np.floor(payouts).sum()
    assert 279 == games.sum()
