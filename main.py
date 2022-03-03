# Jared Tauler 2/25/2022

import yaml
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
DB_BASE = declarative_base()
# DB Setup files:
import lunch_order.database
# Finalize Database
engine = create_engine(CONFIG["db-string"], echo=True)
DB_BASE.metadata.create_all(bind=engine)
DB = sessionmaker(bind=engine)

# List of things to do once ready
ON_READY = []

# Discord
from nextcord.ext import commands
bot = commands.Bot(command_prefix="!")

# Tasks
import lunch_order.main

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for i in ON_READY:
        i.start()

bot.run(CONFIG["token"])
