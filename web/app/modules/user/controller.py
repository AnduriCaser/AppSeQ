from flask import request, request_started, session, render_template, redirect, url_for, Blueprint, Response, current_app, flash
from flask_security import auth_required, permissions_required, roles_accepted, login_required, SQLAlchemySessionUserDatastore, current_user, roles_required
from app.modules.admin import hash_password
from app.modules.user.models import *
from app.db import db_session
import re
from werkzeug.utils import secure_filename
import subprocess


def allowed_file():
    pass


user = Blueprint('user', __name__, url_prefix='/')
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)


@user.route('/dashboard')
@roles_accepted('user')
@auth_required('session')
def dashboard():
    return render_template("user/dashboard.html")


@user.route('/profile')
@roles_accepted('user')
@auth_required('session')
def profile():
    return render_template('user/profile.html', username=current_user.username, points=current_user.points, invite_code=current_user.code_rgstr)


@user.route('/update', methods=['POST'])
@roles_accepted('user')
@auth_required('session')
def update():
    if request.form.get("username") and request.form.get("password") and request.form.get("repassword"):
        username = request.form.get("username")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        if not re.match(r'[A-Za-z0-9]+', username):
            flash("Username only contains numbers and letters !", "warning")

        elif not password == repassword:
            flash("Username only contains numbers and letters !", "warning")

        else:
            user = user_datastore.find_user(id=current_user.id)
            user.password = hash_password(password)
            user.username = username
            db_session.commit()
            flash("Account updated successfully", "success")

            return redirect(url_for('user.profile'))
    return redirect(url_for('user.profile'))


@user.route('/delete/<int:id>')
@roles_accepted('user')
@auth_required('session')
def delete(id):
    if current_user.id == id:
        user = user_datastore.find_user(id=current_user.id)
        user_datastore.delete_user(user)
        db_session.commit()
    else:
        flash(
            "Do not try to delete another ones account or you will get banned !", "danger")
        return render_template('user/profile.html')

    flash("Account deleted successfully", "success")
    return redirect(url_for('auth.logout'))


@user.route("/labs/<string:slug>/start")
@roles_accepted("user")
@auth_required("session")
def labs_start(slug):
    lab = db_session.query(Lab).filter(Lab.slug == slug).one()
    if lab:
        pass



@user.route("/labs/<string:slug>/stop")
@roles_accepted("user")
@auth_required("session")
def labs_stop(slug):
    pass


@user.route('/leaderboard')
@roles_accepted('user')
@auth_required('session')
def leaderboard():
    return render_template('user/leaderboard.html')


@user.route('/purchase', methods=['GET', 'POST'])
@roles_accepted('user')
@auth_required('session')
def purchase():
    return Response("User purchase page")


@user.route('/news')
@roles_required('user')
@auth_required('session')
def news():
    return render_template('user/news.html')


@user.route('/news/create', methods=['POST'])
@roles_required('user')
@permissions_required('user-write')
@auth_required('session')
def create_news():
    pass
