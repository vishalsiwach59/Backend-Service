from backendservice.databaseModels.database import engine
from backendservice.databaseModels.models import Base  # Import your models

# Create all tables in the database
Base.metadata.create_all(bind=engine)
