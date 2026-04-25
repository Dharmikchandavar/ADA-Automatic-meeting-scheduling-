from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# SQLite database URL (creates a local file named 'scheduler.db')
SQLALCHEMY_DATABASE_URL = "sqlite:///./scheduler.db"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed only for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to initialize the database (creates tables based on our models)
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

# Dependency to get a database session for our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()