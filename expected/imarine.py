from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('imarine', __name__, url_prefix='/imarine')


@bp.route('/imarine')
@login_required
def imarine():

    from .visualize.imarine import imarine_spec, spec_table, border_table
    from .visualize.spreadsheet import get_spreadsheet_data, sheet_model, expected_table, real_table, plot, machine_table

    title = 'PAスーパー海物語IN 沖縄5 202509'

    spec = imarine_spec()
    tbl_spec = spec_table(spec)
    tbl_border = border_table(spec)

    machine_name = 'imarine'
    df = get_spreadsheet_data(machine_name)
    sh = sheet_model(df)

    tbl_expected = expected_table(sh, spec)
    tbl_real = real_table(sh)

    plot_img = plot(sh)

    tbl_machine = machine_table(sh, spec)

    return render_template('page_imarine.html', 
                                title = title,
                                tbl_spec = tbl_spec.to_html(classes='tbl-specs'),
                                tbl_border = tbl_border.to_html(classes='tbl-border'),
                                tbl_expected = tbl_expected.to_html(classes='tbl-base', index=False),
                                tbl_real = tbl_real.to_html(classes='tbl-base', index=False),
                                plot_img = plot_img,
                                tbl_machine = tbl_machine.to_html(classes='tbl-machines', index=False)
                            )