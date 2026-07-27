from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://lawncare:localdevpassword@localhost:5432/lawn_care"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
