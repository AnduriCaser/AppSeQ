from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy_utils import PasswordType, EmailType
from datetime import datetime
from flask_security import UserMixin, RoleMixin, AsaList
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

labs_lab_categories = Table(
    "labs_lab_categories",
    Base.metadata,
    Column("labs_id", Integer, ForeignKey("labs.id")),
    Column("lab_category_id", Integer, ForeignKey("lab_categories.id")),
)

challenges_challenge_categories = Table(
    "challenges_challenge_categories",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
    Column("challenge_category_id", Integer, ForeignKey("challenge_categories.id")),
)


class Role(Base, RoleMixin):
    __tablename__ = "roles"

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(MutableList.as_mutable(AsaList()), nullable=True)


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    code_pass = Column(String(255), nullable=False)
    code_rgstr = Column(String(255), nullable=False)
    activated_rgstr_code = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    roles = relationship("Role", secondary=users_roles, backref=backref("users"))
    challenge_comments = relationship("ChallengeComment", backref=backref("users"))
    lab_comments = relationship("LabComment", backref=backref("users"))
    solved_challenges = relationship("SolvedChallenge", backref=backref("users"))
    solved_labs = relationship("SolvedLab", backref=backref("users"))


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    lab_category_id = Column(Integer, ForeignKey("lab_categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    flag = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hints = relationship("LabHint", backref=backref("lab"))
    comments = relationship("LabComment", backref=backref("lab"))


class LabCategory(Base):
    __tablename__ = "lab_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    labs = relationship("Lab", backref=backref("lab_category"))


class ChallengeCategory(Base):
    __tablename__ = "challenge_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    challenges = relationship("Challenge", backref=backref("challenge_category"))


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
    challenge_category_id = Column(Integer, ForeignKey("challenge_categories.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    flag = Column(String(50), nullable=False)
    release_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    stages = relationship("ChallengeStage", backref=backref("challenge"))
    hints = relationship("ChallengeHint", backref=backref("challenge"))
    comments = relationship("ChallengeComment", backref=backref("challenge"))
    solvers = relationship("SolvedChallenge", backref=backref("challenge"))


class ChallengeStage(Base):
    __tablename__ = "challenge_stages"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)


class LabHint(Base):
    __tablename__ = "lab_hints"

    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"))


class ChallengeHint(Base):
    __tablename__ = "challenge_hints"

    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))


class ChallengeComment(Base):
    __tablename__ = "challenge_comments"

    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)


class LabComment(Base):
    __tablename__ = "lab_comments"

    id = Column(Integer, primary_key=True)
    content = Column(String(2555), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
