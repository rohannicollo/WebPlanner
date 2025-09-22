import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import date, datetime

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def status(today, deadline):

    dt1 = today
    dt2 = deadline
    # If before deadline
    if dt1 <= dt2:
        diff = (dt2 - dt1).days

        # Check Status
        if diff == 0:
            return 'Today'
        elif diff == 1:
            return 'Tomorrow'
        elif diff <= 7:
            return 'This Week'
        elif diff > 7 and diff <= 14:
            return 'Next Week'
        elif diff > 14:
            return 'Later'

    # If after deadline
    elif dt1 >= dt2:
        diff = (dt1 - dt2).days

        # Check status
        if diff == 0:
            return 'Today'
        elif diff == 1:
            return 'Missing: Yesterday'
        elif diff <= 7:
            return 'Missing: This Week'
        elif diff > 7 and diff <= 14:
            return 'Missing: Last Week'
        elif diff > 14:
            return 'Missing: Earlier'

        