from database.database import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    task_title = Column(String)
    task_description = Column(String)
    owner_id = Column(Integer)
    status = Column(Boolean, default=False)