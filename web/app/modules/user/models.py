from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy_utils import PasswordType, EmailType
from datetime import datetime
from flask_security import UserMixin, RoleMixin, AsaList
import uuid

from app.db import Base


users_roles = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

users_challenges = Table(
    "users_challenges",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
)

courses_challenges = Table(
    "courses_challenges",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
)

users_labs = Table(
    "users_labs",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("lab_id", Integer, ForeignKey("labs.id")),
)

challenges_labs = Table(
    "challenges_labs",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
    Column("lab_id", Integer, ForeignKey("labs.id")),
)

# labs_categories = Table(
#     "labs_categories",
#     Base.metadata,
#     Column("labs_id", Integer, ForeignKey("labs.id")),
#     Column("category_id", Integer, ForeignKey("categories.id")),
# )

# challenges_categories = Table(
#     "challenges_categories",
#     Base.metadata,
#     Column("challenge_id", Integer, ForeignKey("challenges.id")),
#     Column("category_id", Integer, ForeignKey("categories.id")),
# )


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    code_pass = Column(String(255), default=uuid.uuid4().hex)
    code_rgstr = Column(String(255), default=uuid.uuid4().hex)
    activated_rgstr_code = Column(String(255))
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    roles = relationship("Role", secondary=users_roles, backref=backref("users"))
    comments = relationship("Comment", backref=backref("user"))
    solved_challenges = relationship("SolvedChallenge", backref=backref("user"))
    solved_labs = relationship("SolvedLab", backref=backref("user"))


class Role(Base, RoleMixin):
    __tablename__ = "roles"

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(MutableList.as_mutable(AsaList()), nullable=True)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(2555), nullable=True)
    challenges = relationship(
        "Challenge", secondary=courses_challenges, backref=backref("courses")
    )

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def get_challenges(self, course):
        return [challenge.as_dict() for challenge in course.challenges]


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(2555), nullable=True)
    points = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)
    slug = Column(String(255), default=uuid.uuid4().hex)
    static = Column(Boolean())
    mission_statement = Column(String(3000))
    url = Column(String(255))
    description = Column(String(2000))
    questions = relationship("Question", backref=backref("lab"))
    created_at = Column(DateTime, default=datetime.utcnow)
    comments = relationship("Comment", backref=backref("lab"))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def set_points(self):
        self.points = 0
        for question in self.questions:
            self.points += question.points

    @staticmethod
    def add_spaces(string, *args):
        n_array = []
        for i in args:
            n_array.append(string[:i])
            string = string[i:]
        return " ".join(n_array)


# class Category(Base):
#     __tablename__ = "categories"

#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     description = Column(String(2555), nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     labs = relationship("Challenge", backref=backref("category"))


class SolvedChallenge(Base):
    __tablename__ = "solved_challenges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    solved_at = Column(DateTime, default=datetime.utcnow)


class SolvedLab(Base):
    __tablename__ = "solved_labs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    solved_at = Column(DateTime, default=datetime.utcnow)


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(2555), nullable=False)
    difficulty = Column(String(20))
    points = Column(Integer, default=0)
    #category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    release_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    labs = relationship("Lab", secondary=challenges_labs, backref=backref("challenges"))

    stages = relationship("ChallengeStage", backref=backref("challenge"))
    comments = relationship("Comment", backref=backref("challenge"))
    solvers = relationship("SolvedChallenge", backref=backref("challenge"))

    def __init__(self, name=None, description=None, difficulty=None, points=None):
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.points = points

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_points(self):
        # Get total labs points and set it !
        pass


class ChallengeStage(Base):
    __tablename__ = "challenge_stages"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(2555), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(String(2555), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    lab_id = Column(Integer, ForeignKey("labs.id"))


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"))
    line_number = Column(Integer())
    description = Column(String(2555))
    hint = Column(String(2555))
    answer = Column(String(255), unique=True)
    points = Column(Integer, default=0)

    def __init__(self, description=None, hint=None, answer=None, points=None):
        self.description = description
        self.hint = hint
        self.answer = answer
        self.points = points


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    title = Column(String(1200))
    content = Column(String(2500))
    description = Column(String(2000))

    def __init__(self, name=None, title=None, description=None):
        self.name = name
        self.title = title
        self.description = description
