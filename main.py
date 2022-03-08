# Jared Tauler 2/25/2022
import os
import json
with open('config.json  ', 'r') as f:
    CONFIG = json.load(f)

from nextcord.ext import commands
import nextcord

def custom_id(view: str, id: int) -> str:
    """create a custom id from the bot name : the view : the identifier"""
    return f"{CONFIG['botname']}:{view}:{id}"
# Database
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
def main():
    # Discord
    intents = nextcord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    # load all cogs
    for folder in os.listdir("cogs"):
        if os.path.exists(os.path.join("cogs", folder, "cog.py")):
            bot.load_extension(f"cogs.{folder}.cog")

    bot.run(CONFIG["token"])

if __name__ == "__main__":
    main()
