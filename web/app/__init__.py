from flask import Flask
from celery import Celery
from app.modules.auth.models import *
from app.modules.auth import create_roles
from app.db import init_db, db_session
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    with app.app_context():
        from app.modules.auth.controller import auth

        app.register_blueprint(auth)
    return app


app = create_app()
mail = Mail(app)
csrf = CSRFProtect(app)
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


@app.before_request
def create_db():
    init_db()
    create_roles()
