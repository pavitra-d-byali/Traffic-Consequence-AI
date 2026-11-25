from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    """Create tables and add compatible columns to databases from earlier prototypes."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "complaints" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("complaints")}
        if "review_status" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE complaints ADD COLUMN review_status VARCHAR(20) NOT NULL DEFAULT 'new'"))
