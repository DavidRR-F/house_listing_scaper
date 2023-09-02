from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.base import env

engine = create_engine(env.DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
