from flask_security import SQLAlchemySessionUserDatastore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database


engine = create_engine(
    "mysql+pymysql://root:Tr1234567@127.0.0.1:3306/appseq", pool_size=90)
db_session = scoped_session(sessionmaker(bind=engine))


if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()
Base.query = db_session.query_property()


async def init_db():
    Base.metadata.create_all(bind=engine)


#root:Tr1234567@127.0.0.1:3306