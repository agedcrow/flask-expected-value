from flask import Blueprint, redirect, render_template, url_for
from .auth import login_required

import numpy as np
import pandas as pd


bp = Blueprint('imarine', __name__, url_prefix='/imarine')


@bp.route('/imarine')
@login_required
def imarine():

    from .visualize.imarine import spec, border, result, plot

    title = 'PAスーパー海物語IN 沖縄5 SBA'
    df_border= border()
    df_spec = spec()
    df_result, games, balance = result()
    img_data = plot(games, balance)

    return render_template('page_imarine.html', 
                                title = title,
                                tbl_spec = df_spec.to_html(classes='tbl-spec'),
                                tbl_border = df_border.to_html(classes='tbl-border'),
                                tbl_result = df_result.to_html(classes='tbl-result', index=False),
                                img_data = img_data
                            )