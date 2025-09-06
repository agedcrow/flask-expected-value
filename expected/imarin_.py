from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('imarin_', __name__, url_prefix='/imarin_')


@bp.route('/imarin_')
@login_required
def imarine():

    from .visualize.imarine import imarine_specs, specs_table, border_table
    from .visualize.spreadsheet_ import get_sskey, get_all_records, cutout, theoretical_values, actual_values, plot, machine_table

    title = 'PAスーパー海物語IN 沖縄5 - 202508'
    d = imarine_specs()
    tbl_specs = specs_table(**d)
    tbl_border = border_table(**d)

    machine_name = 'imarin_'
    spreadsheet_key = get_sskey(machine_name)
    df = get_all_records(spreadsheet_key)
    
    args = cutout(df)
    keys = 'ts', 'expected_loop', 'expected_rounds'
    kwargs = {k: d[k] for k in keys}

    tbl_theoretical = theoretical_values(*args, **kwargs)
    tbl_actual = actual_values(*args)
    plot_img = plot(*args)
    tbl_machine = machine_table(df, **kwargs)

    return render_template('page_imarine.html', 
                                title = title,
                                tbl_specs = tbl_specs.to_html(classes='tbl-specs'),
                                tbl_border = tbl_border.to_html(classes='tbl-border'),
                                tbl_result = tbl_theoretical.to_html(classes='tbl-base', index=False),
                                tbl_actual = tbl_actual.to_html(classes='tbl-base', index=False),
                                plot_img = plot_img,
                                tbl_machine = tbl_machine.to_html(classes='tbl-base', index=False)
                            )