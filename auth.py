import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import request
from flask import Response
from flask import session
from flask import url_for
from db import get_db
from models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

def no_login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            flash("You have already logged in.")
            return redirect(url_for("index"))
        return view(**kwargs)
    return wrapped_view

def manager_required(f):   
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        elif g.user.isManager != True:
            return Response("Manager permission required.", status=403, mimetype='application/json')
        return f(*args, **kwargs)
    return decorated_function

def trainer_required(f):   
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        elif g.user.isTrainer != True:
            return Response("Trainer permission required.", status=403, mimetype='application/json')
        return f(*args, **kwargs)
    return decorated_function

def member_required(f):   
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        elif g.user.isMember != True:
            return Response("Member permission required.", status=403, mimetype='application/json')
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):   
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        elif g.user.isManager == False and g.user.isTrainer == False:
            return Response("Staff permission required.", status=403, mimetype='application/json')
        return f(*args, **kwargs)
    return decorated_function

@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    db = get_db()
    if user_id is None or user_type is None:
        g.user = None
    else:
        user = User()
        if user_type == "staff":
            g.db.row_factory.execute('SELECT * FROM Staff WHERE StaffID = %s', (user_id, ))
        else :
            user.isMember = True
            g.db.row_factory.execute('SELECT * FROM Member WHERE MemberID = %s', (user_id, ))
        userData = g.db.row_factory.fetchone()
        user.setData(userData)
        g.user = user

@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        userid = request.form["user_id"]
        userType = request.form["user_type"]
        if userid is None or userType is None:
            flash("Cache error. Please clear your cookies.")
            return redirect(url_for("index"))
        db = get_db()
        user = User()
        error = None
        if userType == "staff":
            g.db.row_factory.execute('SELECT * FROM Staff WHERE StaffID = %s', (userid, ))
        else :
            user.isMember = True
            g.db.row_factory.execute('SELECT * FROM Member WHERE MemberID = %s', (userid, ))
        userData = g.db.row_factory.fetchone()
        if userData is None:
            error = "Incorrect member/staff ID."
        else:
            user.setData(userData)
            if userType == "member" and userData['IsActive'] == 0:
                error = "Deactivated member account."
            g.user = user
        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = userid
            session["user_type"] = userType
            return redirect(url_for("index"))
        flash(error)
    return redirect(url_for("index"))


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
