from flask_security.utils import current_user
from flask_security import (
    SQLAlchemySessionUserDatastore,
    auth_required,
    roles_accepted,
    login_required,
)

from flask_socketio import join_room, leave_room, send, emit
from markupsafe import escape


from app.extensions import socketio


@socketio.on("join_room")
def on_join(data):
    room = data["room"]
    join_room(room)


@socketio.on("message")
def handle_message(data):
    send(data, to=data["room"])


# Challenge ı handle et
@socketio.on("multiple_lab_challenge")
def handle_multiple_lab_challenge(data):
    room_id = data.get("room_id")


# Kullanıcıların bulunduğu odada cevaplar submit edildikçe eğer cevap doğru ise hangi kullanıcı bu cevabı vermişse o gösterilecek
# 2 kullanıcı artı admin bunları görebilecek. Alt kısımda bir chat olacak ve konuşma yapılacak.
@socketio.on("list_answers")
def list_answers(data):
    pass


@socketio.on("challenge_url")
def challenge_url(data):
    pass


@socketio.on("challenge_url")
def end_challlenge_list_answers():
    pass
