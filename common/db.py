from sqlalchemy import create_engine, Column, Integer, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.nhzaselbaerkjmnplsmv:Tushar%406611@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
)

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}  # Very important for Supabase
)
SessionLocal = sessionmaker(bind=engine)

class ChatUser(Base):
    __tablename__ = "chat_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    is_bot = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
