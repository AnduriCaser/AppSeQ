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
    current_app,
)
from flask_security.utils import current_user
from flask_paginate import Pagination, get_page_parameter
from flask_security import (
    SQLAlchemySessionUserDatastore,
    auth_required,
    roles_accepted,
    login_required,
)
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from sqlalchemy.orm.exc import NoResultFound

from app.modules.user.models import *
from app.db import db_session
import requests

common = Blueprint("common", __name__, url_prefix="/common")

# Uygulama içindekiler birbiriyle konuşabilecek

# Admini ekle sorular cevaplandıkça hangi kullanıcının doğru yanıtladığını göreceği bir modal yapısı olacak !


@common.route("/labs/<string:lab_slug>/multiple/challenge/rooms/<string:room_slug>")
@roles_accepted("user", "administrator")
@auth_required("session")
def multiple_lab_challenge_room(lab_slug, room_slug):
    lab = db_session.query(Lab).filter(Lab.slug == lab_slug).first()
    room = db_session.query(LabRoom).filter(LabRoom.room_slug == room_slug).first()
    users = room.users
    role = next((role for role in current_user.roles if role == "administrator"), None)

    if not lab or not room and role != "administrator":
        return redirect(url_for("user.dashboard"))

    # Oda kullanıcıya eklenmemişse !
    if not room in current_user.lab_rooms and role != "administrator":
        return redirect(url_for("user.dashboard"))

    return render_template(
        "common/group.html",
        room_slug=room_slug,
        lab=lab,
        role=role,
    )


@common.route(
    "/labs/<string:lab_slug>/multiple/challenge/rooms/<string:room_slug>/winner"
)
@roles_accepted("user", "administrator")
@auth_required("session")
def multiple_lab_challenge_room_winner(lab_slug, room_slug):
    lab = db_session.query(Lab).filter(Lab.slug == lab_slug).first()
    room = db_session.query(LabRoom).filter(LabRoom.room_slug == room_slug).first()

    return render_template("common/winner.html", lab=lab, room=room)
