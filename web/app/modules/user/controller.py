from flask import (
    request,
    request_started,
    session,
    render_template,
    redirect,
    url_for,
    Blueprint,
    Response,
    current_app,
    flash,
    send_from_directory,
    jsonify,
    abort,
)
from flask_security import (
    auth_required,
    permissions_required,
    roles_accepted,
    login_required,
    SQLAlchemySessionUserDatastore,
    current_user,
    roles_required,
)

from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.orm.exc import NoResultFound
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import redis

from app.modules.admin import hash_password
from app.modules.user.models import *
from app.db import db_session
import re
from werkzeug.utils import secure_filename
import subprocess
from collections import defaultdict


def allowed_file():
    pass


user = Blueprint("user", __name__, url_prefix="/")
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
node_process = None


socketio = SocketIO(current_app)


redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


@user.route("/dashboard")
@roles_accepted("user")
@auth_required("session")
def dashboard():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 1
    offset = (page - 1) * per_page
    courses_count = db_session.query(Course).count()
    labs_count = db_session.query(Lab).count()
    courses = db_session.query(Course).limit(per_page).offset(offset)
    full_courses = db_session.query(Course).all()
    labs = db_session.query(Lab).limit(per_page).offset(offset)

    return render_template(
        "user/dashboard.html", courses=courses, labs=labs, full_courses=full_courses
    )


@user.route("/profile")
@roles_accepted("user")
@auth_required("session")
def profile():
    return render_template(
        "user/profile.html",
        username=current_user.username,
        points=30,
        invite_code=current_user.code_rgstr,
    )


@user.route("/update", methods=["POST"])
@roles_accepted("user")
@auth_required("session")
def update():
    if (
        request.form.get("username")
        and request.form.get("password")
        and request.form.get("repassword")
    ):
        username = request.form.get("username")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        if not re.match(r"[A-Za-z0-9]+", username):
            flash("Username only contains numbers and letters !", "warning")

        elif not password == repassword:
            flash("Username only contains numbers and letters !", "warning")

        else:
            user = user_datastore.find_user(id=current_user.id)
            user.password = hash_password(password)
            user.username = username
            db_session.commit()
            flash("Account updated successfully", "success")

            return redirect(url_for("user.profile"))
    return redirect(url_for("user.profile"))


@user.route("/delete/<int:id>")
@roles_accepted("user")
@auth_required("session")
def delete(id):
    if current_user.id == id:
        user = user_datastore.find_user(id=current_user.id)
        user_datastore.delete_user(user)
        db_session.commit()
    else:
        flash(
            "Do not try to delete another ones account or you will get banned !",
            "danger",
        )
        return render_template("user/profile.html")

    flash("Account deleted successfully", "success")
    return redirect(url_for("auth.logout"))


@user.route("/labs/<string:slug>/view")
@roles_accepted("user")
@auth_required("session")
def view_lab(slug):
    lab = db_session.query(Lab).filter(Lab.slug == slug).first()
    solved_lab = next(
        (
            solved_lab
            for solved_lab in current_user.solved_labs
            if lab.id == solved_lab.id
        ),
        None,
    )
    return render_template(
        "user/dynamic_lab_details.html", lab=lab, solved_lab=solved_lab
    )


@user.route("/labs/<string:slug>/start", methods=["GET"])
@roles_accepted("user", "administrator")
@auth_required("session")
def labs_start(slug):
    global node_process
    lab = db_session.query(Lab).filter(Lab.slug == slug).one()
    if lab and lab.static is False:
        if node_process is None or node_process.poll() is not None:
            node_process = subprocess.Popen(["nodemon", f"{lab.folder}/index.js"])
            return "Application started"

    
    return "Application already started"


@user.route("/labs/<string:slug>/stop", methods=["GET"])
@roles_accepted("user", "administrator")
@auth_required("session")
def labs_stop(slug):
    global node_process
    lab = db_session.query(Lab).filter(Lab.slug == slug).one()
    if lab and lab.static is False:
        if node_process is not None and node_process.poll() is None:
            node_process.terminate()
            node_process = None
            return "Applicaton stopped"

    return "Something went wrong !"


@user.route("/labs/<string:slug>/answer/submit", methods=["POST"])
@roles_accepted("user")
@auth_required("session")
def submit_answer(slug):
    if request.method == "POST":
        data = request.get_json()

        try:
            lab = db_session.query(Lab).filter_by(slug=slug).one()
        except NoResultFound:
            abort(404, description="Lab not found")

        solved_lab = next(
            (
                solved_lab
                for solved_lab in current_user.solved_labs
                if solved_lab.id == lab.id
            ),
            None,
        )

        if not solved_lab:
            solved_lab = SolvedLab()
            current_user.solved_labs.append(solved_lab)

        for q in data:
            question_id = int(q["id"])
            question_value = q["question_value"]

            question = next(
                (
                    question
                    for question in lab.questions
                    if question.id == question_id
                    and question.question_value == question_value
                ),
                None,
            )

            if question:
                if question not in solved_lab.questions:
                    solved_lab.questions.append(question)

        db_session.commit()

        if all(
            target_question in solved_lab.questions for target_question in lab.questions
        ):
            solved_lab.all_solved = True
            db_session.commit()

        return redirect(url_for("user.view_lab", slug=lab.slug))


@user.route("/labs/<string:slug>/download", methods=["GET"])
@roles_accepted("user")
@auth_required("session")
def download_lab_source_code(slug):
    lab = db_session.query(Lab).filter(Lab.slug == slug).one()
    if lab and lab.static == True:
        return send_from_directory(lab.folder, "index.js", as_attachment=True)
    else:
        res = {"error": "Something went wrong"}
        return jsonify(res)


@user.route("/leaderboard")
@roles_accepted("user")
@auth_required("session")
def leaderboard():
    return render_template("user/leaderboard.html")


@user.route("/purchase", methods=["GET", "POST"])
@roles_accepted("user")
@auth_required("session")
def purchase():
    return Response("User purchase page")


@user.route("/news")
@roles_required("user")
@auth_required("session")
def news():
    return render_template("user/news.html")


@user.route("/news/create", methods=["POST"])
@roles_required("user")
@permissions_required("user-write")
@auth_required("session")
def create_news():
    pass


# Challenge başladığı zaman kullanıcılara bu endpoint urli ver çözmeye başlasın !
@user.route("/multiple/labs/<string:lab_slug>/room/<string:room_slug>/challenge")
@roles_required("user")
@auth_required("session")
def multiple_lab_challenge_screen(lab_slug, room_slug):
    lab = db_session.query(Lab).filter(Lab.slug == lab_slug).first()
    room = db_session.query(LabRoom).filter(LabRoom.room_slug == room_slug).first()

    if room not in lab.lab_rooms:
        abort(404, description="Lab isn't attend to this room")

    solved_lab = next(
        (
            solved_lab
            for solved_lab in current_user.solved_labs
            if lab.id == solved_lab.id
        ),
        None,
    )
    return render_template(
        "common/multiple_lab_challenge.html", lab=lab, solved_lab=solved_lab, room=room
    )


# İki kullanıcının soruları soruların cevabını submit edeceği kısım. Doğru cevaplayanın inputu borderı yeşil
# yanlış cevaplayanın ya da geç kalanın input disabled olacak.


@user.route(
    "/multiple/labs/<string:lab_slug>/room/<string:room_slug>/answer/submit",
    methods=["POST"],
)
@roles_accepted("user")
@auth_required("session")
def multiple_lab_challenge_submit_answer(lab_slug, room_slug):
    if request.method == "POST":
        data = request.get_json()
        
        print(data)

        try:
            lab = db_session.query(Lab).filter_by(slug=lab_slug).first()
            room = db_session.query(LabRoom).filter_by(room_slug=room_slug).first()
            users = room.users

        except NoResultFound:
            abort(404, description="Lab or room not found")

        if room not in lab.lab_rooms:
            abort(404, description="Lab isn't attend to this room")

        # algoritmayı sonra düzelt
        solved_lab = next(
            (
                solved_lab
                for user in users
                for solved_lab in user.solved_labs
                if solved_lab.id == lab.id
            ),
            None,
        )

        if not solved_lab:
            solved_lab = SolvedLab()
            for user in users:
                user.solved_labs.append(solved_lab)

        for q in data:
            question_id = int(q["id"])
            question_value = str(q["question_value"])
            
            print(question_id, question_value)

            question = next(
                (
                    question
                    for question in lab.questions
                    if question.id == question_id and str(question.question_value) == question_value  # Ensure correct type comparison
                ),
                None,
            )
            

            if question:
                question_key = f"question_{question.id}_solved"

                if not redis_client.exists(question_key):
                    redis_client.set(question_key, current_user.id)
                    if question not in solved_lab.questions:
                        question.solved_by = current_user
                        solved_lab.questions.append(question)

            db_session.commit()

            emit(
                "trace_answers",
                {"question_id": question_id, "solved_by": question.solved_by.username},
                broadcast=True,
                namespace="/",
            )

        if all(
            target_question in solved_lab.questions for target_question in lab.questions
        ):
            solved_lab.all_solved = True
            
            user_scores = defaultdict(int)

            for q in solved_lab.questions:
                user_scores[q.solved_by] += q.question_point

            max_score = 0
            room_winner = None

            for user, score in user_scores.items():
                if score > max_score:
                    max_score = score
                    room_winner = user

            room.winner = room_winner
            
            db_session.commit()

            emit(
                "end_challenge",
                {"message": "Challenge is done", "winner": "Deneme"},
                broadcast=True,
                namespace="/",
            )

        return redirect(
            url_for(
                "user.multiple_lab_challenge_screen",
                lab_slug=lab.slug,
                room_slug=room.room_slug,
            )
        )
