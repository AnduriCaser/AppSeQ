from flask_security import SQLAlchemySessionUserDatastore
from app.modules.user.models import *
from app.db import db_session
from slugify import slugify
import hashlib
import uuid
import os

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../../labs"))


print(basedir)

ADMIN = {
    "username": "admin",
    "email": "admin@gmail.com",
    "password": "asfmqşweo12314",
}

LABS = [
    {
        "name": "Union Based SQL Injection",
        "url": "http://localhost:3000",
        "folder": "None",
        "static": False,
    },
    {"name": "JWT 1", "url": "None", "folder": f"{basedir}/JWT 1", "static": True},
    {
        "name": "Cache Poisoning",
        "url": "None",
        "folder": f"{basedir}/Union_Based_SQL_Injection",
        "static": True,
    },
]


async def create_labs():
    if db_session.query(Lab).count() == 0:
        for g in LABS:
            lab = Lab(
                name=g.get("name"),
                url=g.get("url"),
                folder=g.get("folder"),
                static=g.get("static"),
            )
            db_session.add(lab)
            db_session.commit()


async def create_admin():
    if not user_datastore.find_user(email=ADMIN.get("email")):
        user_datastore.create_user(
            username=ADMIN.get("username"),
            email=ADMIN.get("email"),
            password=hash_password(ADMIN.get("password")),
            code_pass=str(uuid.uuid4().hex),
        )
        db_session.commit()


async def set_admin_role():
    if not user_datastore.find_user(email=ADMIN.get("email")).has_role("administrator"):
        user = user_datastore.find_user(email=ADMIN.get("email"))
        role = user_datastore.find_role("administrator")
        user_datastore.add_role_to_user(user, role)
        db_session.commit()


def hash_password(password):
    salt = "162886609164245863786468725781264657609"
    key = "%s%s" % (salt, password)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
