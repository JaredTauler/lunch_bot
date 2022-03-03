from __main__ import DB_BASE
from sqlalchemy import Column, Integer, String

class Guild(DB_BASE):
    __tablename__ = "guild"

    id = Column("id", String, primary_key=True)
    announce_channel = Column("announce_channel", String, unique=True)
    ping_role = Column("ping_role", String, unique=True)
