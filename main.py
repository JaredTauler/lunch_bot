# Jared Tauler 2/25/2022

import yaml
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

# List of things to do once ready
READY = []

# Discord
from nextcord.ext import commands
bot = commands.Bot(command_prefix="!")

# Tasks
from task.order_lunch import order_lunch

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for i in READY:
        i.start()

@bot.event
async def on_message(message):
    if message.author.id != bot.user.id: # Message is not from bot
        if message.content[0] == "!": # Message is a command
            if message.content == "!lunch":
                await order_lunch(message)

bot.run(CONFIG["token"])

