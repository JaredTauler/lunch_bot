from __main__ import CONFIG
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Guild(Base):
	__tablename__ = "guild"

	id = Column("id", String, primary_key=True)
	announce_channel = Column("announce_channel", String, unique=True)

engine = create_engine('sqlite:///db.db', echo=True)

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
