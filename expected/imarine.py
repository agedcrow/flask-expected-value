from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('imarine', __name__, url_prefix='/imarine')


@bp.route('/imarine')
@login_required
def imarine():

    from .visualize.imarine import imarine_specs, specs_table, border_table
    from .visualize.spreadsheet import get_spreadsheet_data, work, tables, plot, machine_table

    title = 'PAスーパー海物語IN 沖縄5 202509 -'

    specs = imarine_specs()
    tbl_specs = specs_table(**specs)
    tbl_border = border_table(**specs)

    machine_name = 'imarine'
    df = get_spreadsheet_data(machine_name)

    t = work(df)
    tbl_theoretical, tbl_actual = tables(*t, **specs)
    plot_img = plot(*t)

    tbl_machine = machine_table(df, **specs)

    return render_template('page_imarine.html', 
                                title = title,
                                tbl_specs = tbl_specs.to_html(classes='tbl-specs'),
                                tbl_border = tbl_border.to_html(classes='tbl-border'),
                                tbl_result = tbl_theoretical.to_html(classes='tbl-base', index=False),
                                tbl_actual = tbl_actual.to_html(classes='tbl-base', index=False),
                                plot_img = plot_img,
                                tbl_machine = tbl_machine.to_html(classes='tbl-machines', index=False)
                            )