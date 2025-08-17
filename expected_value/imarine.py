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

    from .visualize.gspreadsheet import get_sskey, get_all_records, df2dict, stat_for_starts

    title = 'PAスーパー海物語IN 沖縄5 SBA'
    m = specs()
    tbl_specs = specs_table(m)
    tbl_border = border_table(m)

    KEY = 'imarine'
    starts, rounds, payouts, games = arrays_from_sheet(KEY)
    tbl_result = result(starts, rounds, payouts, games, **m.model_dump())
    data = plot_data(starts, rounds, payouts, games)
    plot_img = plot(*data)

    sskey = get_sskey(KEY)
    df = get_all_records(sskey)
    d = df2dict(df)
    machine_stats = stat_for_starts(d)
    
    return render_template('page_imarine.html', 
                                title = title,
                                tbl_specs = tbl_specs.to_html(classes='tbl-specs'),
                                tbl_border = tbl_border.to_html(classes='tbl-border'),
                                tbl_result = tbl_result.to_html(classes='tbl-result', index=False),
                                plot_img = plot_img,
                                machine_stats = machine_stats
                            )