# init_db.py

from app.database import engine, Base
from app.models import Expense, Budget  # must import so Base "sees" them

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done! Tables created.")
