from flask import (
    flash,
    redirect,
    url_for,
    render_template,
    request,
    Blueprint,
    Response,
    jsonify,
    json,
)
from flask import current_app
from flask_security.utils import current_user
from flask_paginate import Pagination, get_page_parameter
from flask_security import (
    SQLAlchemySessionUserDatastore,
    auth_required,
    roles_accepted,
    login_required,
)
from sqlalchemy.orm.exc import NoResultFound

from app.db import db_session
from app.modules.user.models import users_roles
from app.modules.user.models import Role, User
from app.modules.user.models import Challenge, Lab, Question, Course
import re

admin = Blueprint("admin", __name__, url_prefix="/admin")

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)


@admin.route("/dashboard")
@auth_required("session")
@roles_accepted("administrator")
def dashboard():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 1
    offset = (page - 1) * per_page
    courses_count = db_session.query(Course).count()
    labs_count = db_session.query(Lab).count()
    courses = db_session.query(Course).limit(per_page).offset(offset)
    full_courses = db_session.query(Course).all()
    labs = db_session.query(Lab).limit(per_page).offset(offset)
    course_paginate = Pagination(
        page=page,
        per_page=per_page,
        total=courses_count,
        offset=offset,
        css_framework="bootstrap5",
        show_single_page=True,
    )
    lab_paginate = Pagination(
        page=page,
        per_page=per_page,
        total=labs_count,
        courses=courses,
        offset=offset,
        css_framework="bootstrap5",
        show_single_page=True,
    )
    return render_template(
        "admin/dashboard.html",
        course_paginate=course_paginate,
        lab_paginate=lab_paginate,
        courses=courses,
        labs=labs,
        full_courses = full_courses
    )


@admin.route("/profile")
@auth_required("session")
@roles_accepted("administrator")
def profile():
    return render_template("admin/profile.html")


def get_labs(page, per_page=3):
    offset = (page - 1) * per_page
    labs = db_session.query(Lab).limit(per_page).offset(offset)
    return [lab.as_dict() for lab in labs]


@admin.route("/api/labs", methods=["GET", "POST"])
@auth_required("session")
@roles_accepted("administrator")
def api_labs():
    try:
        if request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid input format"}), 400

            result = (
                get_labs(data.get("page", 1))
                if isinstance(data, dict)
                else [
                    lab.as_dict()
                    for lab in db_session.query(Lab).filter(Lab.name.in_(data)).all()
                ]
            )
            return jsonify(result)

    except Exception as e:
        status = {"error": "Something went wrong"}
        return jsonify(status)


@admin.route("/courses/<string:slug>")
@auth_required("session")
@roles_accepted("administrator")
def courses(slug):
    course = db_session.query(Course).filter(Course.slug == slug).first()
    challenges = course.challenges
    return render_template("admin/course.html", challenges=challenges, course=course)


@admin.route("/course/create", methods=["GET", "POST"])
@auth_required("session")
@roles_accepted("administrator")
def create_course():
    status = {}
    if request.method == "POST":
        try:
            data = request.get_json()

            course_name = data.get("name")
            course_description = data.get("description")
            challenges = data.get("challenges")

            if not course_name or not re.match("^[A-Za-z0-9\s]*$", course_name):
                flash("Invalid course name !", "danger")
                return redirect(url_for("admin.create_course"))

            if not course_description or not re.match(
                "^[A-Za-z0-9\s]*$", course_description
            ):
                flash("Invalid course description !", "danger")
                return redirect(url_for("admin.create_course"))

            for challenge in challenges:
                if not challenge.get("name") or not re.match(
                    "^[A-Za-z0-9\s]*$", challenge.get("name")
                ):
                    flash("Invalid challenge name !", "danger")
                    return redirect(url_for("admin.create_course"))

                if not challenge.get("description") or not re.match(
                    "^[A-Za-z0-9\s]*$", challenge.get("description")
                ):
                    flash("Invalid challenge description !", "danger")
                    return redirect(url_for("admin.create_course"))

                for ix, lab in enumerate(challenge.get("labs")):
                    if db_session.query(Lab).filter(Lab.name == lab):
                        if (ix + 1) == len(challenge.get("labs")):
                            status.__setitem__("result", "success")
                    else:
                        flash("Invalid lab name !", "danger")
                        return redirect(url_for("admin.create_course"))

            if status.get("result") == "success":
                course = Course(course_name, course_description)
                for challenge in challenges:
                    cy_challenge = Challenge(
                        challenge.get("name"), challenge.get("description")
                    )
                    for lab in challenge.get("labs"):
                        cy_lab = db_session.query(Lab).filter(Lab.name == lab).first()
                        cy_challenge.labs.append(cy_lab)
                    course.challenges.append(cy_challenge)
                    db_session.add(cy_challenge)

                db_session.add(course)
                db_session.commit()

                flash("Course created successfully !", "success")
                return redirect(url_for("admin.create_course"))
        except Exception as e:
            print(e)
            res = {"error": "Something went wrong"}
            return jsonify(res)

    return render_template("admin/course_create.html")


# Lab kısımlarını bitirdikten sonra burayı bitir


@admin.route("/courses/<string:slug>/edit", methods=["GET", "POST"])
@auth_required("session")
@roles_accepted("administrator")
def edit_course(slug):
    if request.method == "POST":
        pass

    course = db_session.query(Course).filter(Course.slug == slug).first()
    return render_template("admin/course_create.html")


# Genel istatistik ve kullanıcı istatistiklerini oluştur


@admin.route("/general/statistics")
@auth_required("session")
@roles_accepted("administrator")
def general_statistics():
    users = (
        User.query.join(users_roles)
        .join(Role)
        .filter((users_roles.c.user_id == User.id) & users_roles.c.role_id == Role.id)
        .filter(Role.name != "administrator")
    )

    labs = db_session.query(Lab)

    return render_template("admin/general_statistics.html", users=users, labs=labs)


@admin.route("/statistics/user/<int:id>")
@auth_required("session")
@roles_accepted("administrator")
def user_statistics(id):
    # Bu kısımda kullanıcının çözdüğü lablarla alakalı genel bir istatistik oluştur ama en son !!!
    user = user_datastore.find_user(id=id)
    return Response("User Statistics", user=user)


# Package kısmına labları bitirdikten sonra karar ver


@admin.route("/package/create", methods=["GET", "POST"])
@auth_required("session")
@roles_accepted("administrator")
def create_package():
    return Response("Package Create")


# Course kısımlarını bitirince lab ksımına geç !!!


@admin.route("/labs/<string:slug>")
@auth_required("session")
@roles_accepted("administrator")
def labs(slug):
    lab = db_session.query(Lab).filter(Lab.slug == slug).first()
    return render_template("admin/lab.html", lab=lab)


@admin.route("/labs/<string:slug>/edit", methods=["GET", "POST"])
@auth_required("session")
@roles_accepted("administrator")
def edit_labs(slug):
    try:
        lab = db_session.query(Lab).filter_by(slug=slug).one()
    except NoResultFound:
        flash("Lab not found", "danger")
        return redirect(url_for("admin.labs"))

    if request.method == "POST":

        def is_valid_input(value, regex, message):
            if not (value and regex.match(value)):
                flash(message, "danger")
                return False
            return True

        input_fields = [
            ("lab_name", r"^[A-Za-z0-9\s]*$", "Invalid lab name!"),
            (
                "lab_description",
                r"^[A-Za-z0-9\s\.,!?'\"\-\(\)]*$",
                "Invalid lab description!",
            ),
            ("difficulty", r"^[0-9]|10$", "Invalid lab difficulty!"),
            (
                "lab_mission_statement",
                r"^[A-Za-z0-9\s\.,!/=?'\"\-\(\)]*$",
                "Invalid lab mission statement!",
            ),
        ]

        input_checks = [
            is_valid_input(request.form[field], re.compile(pattern), message)
            for field, pattern, message in input_fields
        ]

        if not all(input_checks):
            return redirect(url_for("admin.edit_labs", slug=lab.slug))
        

        field_names = ["question_description", "question_hint", "question_value", "question_point"]
        
        
        lab.update({attr: request.form.get(f) for attr, f in [("name", "lab_name"), ("description", "lab_description"), ("difficulty", "difficulty"), ("mission_statement", "lab_mission_statement")]})

    
        lab.questions = [
            Question(
                **{field: request.form.getlist(field + '[]')[i] for field in field_names}
            )
            for i in range(len(request.form.getlist(f"{field_names[0]}[]")))
        ]

        db_session.commit()

        flash("Lab edited successfully!", "success")
        return redirect(url_for("admin.labs", slug=lab.slug))

    return render_template("admin/edit_lab.html", lab=lab)


# User update , delete and create method will add later (not important now)


@admin.route("/add/user")
@auth_required("session")
@roles_accepted("administrator")
def add_user():
    pass


@admin.route("/delete/user/<int:id>")
@auth_required("session")
@roles_accepted("administrator")
def delete_user(id):
    pass


@admin.route("/update/user/<int:id>")
@auth_required("session")
@roles_accepted("administrator")
def update_user(id):
    pass
