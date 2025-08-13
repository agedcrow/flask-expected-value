from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('agnes4', __name__, url_prefix='/agnes4')


@bp.route('/agnes4')
@login_required
def agnes4():

    from .visualize.agnes4 import specs, specs_table, border_tables
    from .visualize.gspreadsheet import arrays_from_sheet, result, plot_data, plot

    title = 'PA大海物語4スペシャル RBA'
    kw = specs()
    tbl_specs = specs_table(**kw)

    games = 0, 33, 53, 90, 120, 160, 190
    dfs = border_tables(*games, **kw)

    tbl_borders = []
    for game, df in zip(games, dfs):
        cap = str(game) +  ' game'
        tbl = df.to_html(classes='tbl-border')
        tbl_borders.append((cap, tbl))

    KEY = 'agnes4'
    starts, rounds, payouts, games = arrays_from_sheet(KEY)
    tbl_result = result(starts, rounds, payouts, games, **kw)
    print(tbl_result)
    data = plot_data(starts, rounds, payouts, games)
    plot_img = plot(*data)

    return render_template('page_agnes4.html', 
                                title = title,
                                tbl_specs = tbl_specs.to_html(classes='tbl-specs'),
                                tbl_borders = tbl_borders,
                                tbl_result = tbl_result.to_html(classes='tbl-result', index=False),
                                plot_img = plot_img
                            )