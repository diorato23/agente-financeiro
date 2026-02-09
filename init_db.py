from backend.database import engine
from backend import models

print("Creating tables...")
models.Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
