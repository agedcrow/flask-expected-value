# import pytest


# @pytest.fixture
# def sheet(app):
#     with app.app_context():
#         from expected_value.visualize import spreadsheet
#         return spreadsheet

# KEY = 'test_seastory'

import os
from expected.visualize import spreadsheet


def test_reference_files():
    assert os.path.exists(spreadsheet.TOKEN_FILE)
    assert os.path.exists(spreadsheet.SSKEY_FILE)


def test_get_spreadsheet_key():
    machine_name = 'marine'
    # print(dir(spreadsheet))
    key = spreadsheet.get_spreadsheet_key(machine_name)
    assert key == ''


def test_connect_gspread():
    assert 1


def test_ws2df():
    assert 1


def test_get_spreadsheet_data():
    assert 1



def test_get_rate():
    # x.get_rate(start, payout, **specs)
    assert 1

