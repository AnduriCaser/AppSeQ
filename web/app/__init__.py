from flask import Flask
from celery import Celery
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_cors import CORS
import asyncio



from app.modules.user.models import User, Role
from app.modules.auth import create_roles
from app.modules.admin import create_admin, set_admin_role, create_labs
from app.db import init_db, db_session
from app.modules.common.events import socketio


async def async_before_request():
    await init_db()
    await create_roles()
    await create_admin()
    await set_admin_role()
    await create_labs()


def create_app():
    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.config.from_object("config")

    with app.app_context():
        asyncio.run(async_before_request())
        from app.modules.auth.controller import auth
        from app.modules.user.controller import user
        from app.modules.admin.controller import admin
        from app.modules.common.controller import common

        app.register_blueprint(auth)
        app.register_blueprint(user)
        app.register_blueprint(admin)
        app.register_blueprint(common)
        
        socketio.init_app(app)

    return app


app = create_app()
mail = Mail(app)
csrf = CSRFProtect(app)
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)

