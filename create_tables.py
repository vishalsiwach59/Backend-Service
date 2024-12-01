from backendservice.databaseModels.database import engine, sessionmaker
from backendservice.databaseModels.models import Base  # Import your models
from backendservice.auth.seed_permissions import seed_permissions

# Create all tables in the database
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
seed_permissions(db)