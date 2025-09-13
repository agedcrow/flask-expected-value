from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('agnes4', __name__, url_prefix='/agnes4')


@bp.route('/agnes4')
@login_required
def agnes4():

    from .visualize.agnes4 import agnes4_spec, spec_table, border_tables
    from .visualize.spreadsheet import get_spreadsheet_data, sheet_model, expected_utime_table, real_table, plot, machine_table

    title = 'PA大海物語4スペシャル RBA 202509'
    spec = agnes4_spec()
    tbl_spec = spec_table(spec)

    sg = 34, 54, 80, 110, 140, 170
    dfs = border_tables(spec, *sg)

    tbl_borders = []
    for g, df in zip(sg, dfs):
        cap = str(g) +  ' game'
        tbl = df.to_html(classes='tbl-border')
        tbl_borders.append((cap, tbl))

    machine_name = 'agnes4'
    df = get_spreadsheet_data(machine_name)
    sh = sheet_model(df)

    tbl_expected = expected_utime_table(sh, spec)
    tbl_real = real_table(sh)

    plot_img = plot(sh)

    tbl_machine = machine_table(sh, spec)

    return render_template('page_agnes4.html', 
                                title = title,
                                tbl_spec = tbl_spec.to_html(classes='tbl-specs'),
                                tbl_borders = tbl_borders,
                                tbl_expected = tbl_expected.to_html(classes='tbl-base', index=False),
                                tbl_real = tbl_real.to_html(classes='tbl-base', index=False),
                                plot_img = plot_img,
                                tbl_machine = tbl_machine.to_html(classes='tbl-machines', index=False)
                            )