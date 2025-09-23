from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./papers.db"  

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---- Paper table ----
class Paper(Base):
    __tablename__ = "papers"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)  

# ---- User table ----
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---- Create tables ----
Base.metadata.create_all(bind=engine)
