import os
from sqlmodel import create_engine, SQLModel

sqlite_file_name = "gymprogress.db"
sqllite_url = f"sqlite:///{sqlite_file_name}"
db_url = os.environ.get("DATABASE_URL",sqllite_url)


if db_url and db_url.startswith("postgres://"):
	db_url = db_url.replace("postgres://","postgresql://",1)


engine = create_engine(db_url)

def create_file_db():
	SQLModel.metadata.create_all(engine)
