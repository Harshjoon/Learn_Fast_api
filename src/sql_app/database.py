from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

'''
WHAT ARE WE DOING HERE ?
- connecting to a sqlite database.
- db created will be located in the same directory.
- The argument 'connect_args={"check_same_thread":False}' is needed
  only for sqlite databases.
- Each instance of the session local class will be a database session.
'''

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()