from flask_security import SQLAlchemySessionUserDatastore
from app.modules.auth.models import Role, User
from app.db import db_session

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)

ROLES = [{"name": "administrator"}, {"name": "user"}]


def create_roles():
    if db_session.query(Role).count() != len(ROLES):
        for role in ROLES:
            user_datastore.create_role(name=role.get("name"))
            db_session.commit()

