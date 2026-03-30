from sqlmodel import SQLModel, Session, create_engine
import os

# On utilise le dossier /app/data défini dans ton docker-compose
sqlite_url = "sqlite:////app/data/budget.db"

# connect_args={"check_same_thread": False} est OBLIGATOIRE pour SQLite avec FastAPI
engine = create_engine(
    sqlite_url, 
    echo=True, 
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    # Maintenant SQLModel est bien défini grâce à l'import en ligne 1
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
