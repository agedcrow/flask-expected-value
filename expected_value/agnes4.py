from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('agnes4', __name__, url_prefix='/agnes4')


@bp.route('/agnes4')
@login_required
def agnes4():

    from .visualize.agnes4 import spec, border

    title = 'PA大海物語4スペシャル RBA'
    df_spec = spec()

    dfs_border, start_games = border()
    borders = [] 
    for sg, df_border in zip(start_games, dfs_border):
        start_game = str(sg) + ' game'
        tbl = df_border.to_html(classes='tbl-border')
        borders.append((start_game, tbl))


    # df_result, games, balance = result()
    # img_data = plot(games, balance)

    return render_template('page_agnes4.html', 
                                title = title,
                                tbl_spec = df_spec.to_html(classes='tbl-spec'),
                                tbl_borders=borders,
                                # tbl_result = df_result.to_html(classes='tbl-result', index=False),
                                # img_data = img_data
                            )