from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class Guild(base):
    __tablename__ = "guild"

    id = Column("id", String, primary_key=True)
    announce_channel = Column("announce_channel", String, unique=True)
    ping_role = Column("ping_role", String, unique=True)


class Database():
    def __init__(self, dbstring):

        # Finalize Database
        engine = create_engine(dbstring, echo=True)
        base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)

