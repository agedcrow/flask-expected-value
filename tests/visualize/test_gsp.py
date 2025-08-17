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


def test_arrr(gss):
    res = gss.arrr('test_seastory')
    print(res)
    assert True