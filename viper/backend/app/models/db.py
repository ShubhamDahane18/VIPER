from sqlmodel import SQLModel, create_engine, Session
from app.models.schema import User, Meeting, AuditLog, ActionItem
import os

# Use SQLite for prototype, easy to swap to PostgreSQL later via env URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./viper_mvp.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        from sqlmodel import select
        # Add demo users if not present
        if not session.exec(select(User)).first():
            demo_users = [
                User(username="admin_user", role="admin"),
                User(username="legal_user", role="legal"),
                User(username="eng_user", role="engineering"),
                User(username="sales_user", role="sales"),
                User(username="rahul", role="engineering"), # Specific user for action items
            ]
            session.add_all(demo_users)
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session
