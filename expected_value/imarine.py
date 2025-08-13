from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('imarine', __name__, url_prefix='/imarine')


@bp.route('/imarine')
@login_required
def imarine():

    from .visualize.imarine import specs, specs_table, border_table
    from .visualize.gspreadsheet import arrays_from_sheet, result, plot_data, plot

    title = 'PAスーパー海物語IN 沖縄5 SBA'
    kw = specs()
    tbl_specs = specs_table(**kw)
    tbl_border = border_table(**kw)

    KEY = 'imarine'
    starts, rounds, payouts, games = arrays_from_sheet(KEY)
    tbl_result = result(starts, rounds, payouts, games, **kw)
    data = plot_data(starts, rounds, payouts, games)
    plot_img = plot(*data)

    return render_template('page_imarine.html', 
                                title = title,
                                tbl_specs = tbl_specs.to_html(classes='tbl-specs'),
                                tbl_border = tbl_border.to_html(classes='tbl-border'),
                                tbl_result = tbl_result.to_html(classes='tbl-result', index=False),
                                plot_img = plot_img
                            )