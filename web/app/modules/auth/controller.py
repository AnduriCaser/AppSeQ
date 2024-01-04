from flask import (
    redirect,
    url_for,
    session,
    Blueprint,
    render_template,
    request,
    flash,
    current_app,
    Response,
    abort,
)
from flask_security import SQLAlchemySessionUserDatastore
from app.modules.auth.models import *
from app.modules.admin import hash_password
import re
import uuid
from app.db import db_session
from flask_security.utils import login_user, logout_user, current_user
from flask_mail import Mail, Message
from app.modules.user.models import User, Role, users_roles

auth = Blueprint("auth", __name__, url_prefix="/auth")

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
mail = Mail(current_app)


def email_sender(email, html):
    msg = Message("CyberPath Reset Password", recipients=[email], html=html)
    try:
        mail.send(msg)
    except Exception as e:
        raise Exception("Something went wrong !")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = user_datastore.find_user(email=email)
        if user is not None and user.password == hash_password(password):
            login_user(user, remember=True)

            flash("Login successfully", "success")
            if (
                User.query.join(users_roles)
                .join(Role)
                .filter(
                    (users_roles.c.user_id == User.id)
                    & (users_roles.c.role_id == Role.id)
                )
                .filter((User.id == current_user.id) & (Role.name == "administrator"))
                .first()
                is not None
            ):
                return redirect("/admin/dashboard")
            else:
                return redirect("/dashboard")

    return render_template("auth/sign-in.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if (
        request.method == "POST"
        and request.form.get("username")
        and request.form.get("email")
        and request.form.get("password")
    ):
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        user = user_datastore.find_user(email=email)

        if user:
            flash("User already exists !", "warning")

        elif password != confirm_password:
            flash("Passwords do not match !", "warning")

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address !", "warning")

        elif not re.match(r"[A-Za-z0-9]+", username):
            flash("Username only contains numbers and letters !", "warning")

        elif not username or not email or not password or not confirm_password:
            flash("Please fill out the form !", "warning")
        else:
            if request.form.get("invite"):
                invite_code = request.form.get("invite")
                user = user_datastore.find_user(code_rgstr=invite_code)
                if user:
                    new = user_datastore.create_user(
                        username=username,
                        email=email,
                        password=hash_password(password),
                        code_pass=str(uuid.uuid4().hex),
                        code_rgstr=str(uuid.uuid4().hex),
                        activated_rgstr_code=invite_code,
                    )
                    role = user_datastore.find_role("user")
                    user_datastore.add_role_to_user(new, role)
                    user.points += 20
                    db_session.commit()
                    flash("Registration completed", "success")
                    return redirect(url_for("auth.login"))
                else:
                    flash("Invalid Code !", "danger")
                    return redirect(url_for("auth.login"))
            else:
                user = user_datastore.create_user(
                    username=username,
                    email=email,
                    password=hash_password(password),
                    code_pass=str(uuid.uuid4().hex),
                    code_rgstr=str(uuid.uuid4().hex),
                )
                role = user_datastore.find_role("user")
                user_datastore.add_role_to_user(user, role)
                db_session.commit()
                flash("Registration completed", "success")
                return redirect(url_for("auth.login"))

    return render_template("auth/sign-up.html")


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST" and request.form.get("email"):
        email = request.form.get("email")
        user = user_datastore.find_user(email=email)
        if user is not None:
            password_reset_url = url_for(
                "auth.reset_password", code=user.code_pass, _external=True
            )
            html = render_template(
                "auth/email_reset.html", password_reset_url=password_reset_url
            )

            try:
                email_sender("carlosthier89@gmail.com", html)
                flash("Reset request sent. Check your email.", "success")
                return render_template("auth/password-reset.html")
            except Exception:
                return abort(500)

        else:
            flash("There is no such email !", "danger")
    return render_template("auth/password-reset.html")


@auth.route("/reset/<string:code>", methods=["GET", "POST"])
def reset_password(code):
    try:
        user = user_datastore.find_user(code_pass=code)
        if user is None:
            raise Exception
        if request.method == "POST":
            if (
                user is not None
                and request.form.get("password")
                and request.form.get("confirm-password")
            ):
                new_password = request.form.get("password")
                confirm_password = request.form.get("confirm-password")

                if new_password == confirm_password:
                    user.password = hash_password(new_password)
                    user.code_pass = str(uuid.uuid4().hex)

                    db_session.commit()
                    flash("Password changed correctly", "success")
                    return redirect(url_for("auth.login"))

                flash("Passwords don't match !", "warning")
                return render_template("auth/new-password.html")
            flash("Fill the blanks !", "warning")
            return render_template("auth/new-password.html")
        return render_template("auth/new-password.html")
    except Exception:
        return abort(400)


# İsteğe bağlı belki passwordless login işlemi yapılırsa kullanılacak
@auth.route("/magic")
def magic_link():
    pass


@auth.route("/logout")
def logout():
    logout_user()
    flash("Logout Successfully !")
    return redirect(url_for("auth.login"))
