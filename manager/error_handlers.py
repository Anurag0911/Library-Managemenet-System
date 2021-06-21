from . import app

from flask import render_template, request
from flask_login import current_user

@app.errorhandler(404)
def not_found(e):
    """Function for running MUSICA algorithm
    Parameters
    ----------
    e: not fount error
        404

    Returns
    -------
    404:
        404 template
    """
    return render_template("404.html", user=current_user)