from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Create a connection to the database

engine = create_engine('postgresql://postgres:root123@localhost:5432/delivery_db', echo=True)

Base = declarative_base()
session = sessionmaker(bind=engine)