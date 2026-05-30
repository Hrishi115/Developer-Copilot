from database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    ingest_query_count = Column(Integer, default=0)
    retrieval_query_count = Column(Integer, default=0)
    query_reset_at = Column(DateTime(timezone = True), default=datetime.now(timezone.utc))