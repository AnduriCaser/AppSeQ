from flask_security import SQLAlchemySessionUserDatastore
from app.modules.auth.models import Role, User
from app.db import db_session

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)


class UserNotFound(Exception):

    def __init__(self, user):
        pass
