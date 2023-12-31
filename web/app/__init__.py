from flask import Flask
from celery import Celery
from app.modules.user.models import User, Role
from app.modules.auth import create_roles
from app.modules.admin import create_admin, set_admin_role, create_labs
from app.db import init_db, db_session
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    with app.app_context():
        from app.modules.auth.controller import auth
        from app.modules.user.controller import user
        from app.modules.admin.controller import admin

        app.register_blueprint(auth)
        app.register_blueprint(user)
        app.register_blueprint(admin)

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
    create_admin()
    set_admin_role()
    create_labs()
