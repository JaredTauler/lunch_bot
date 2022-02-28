# Jared Tauler 2/25/2022

import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

import os
import random
import schedule
import requests

# Discord
# from nextcord.ext import commands
from nextcord.ui import Button, View, Select
import nextcord
bot = nextcord.Client()

# Anvil
from anvil_wrapper import lunch_to_server, auth as anvil_auth
anvil_auth(config["anvil-token"])

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

async def order_lunch(message):
    async def place_order(interaction, milk):
        uid = interaction.user.id
        res = lunch_to_server(uid, milk)  # Make API call.

        if res == 1:  # Success
            await interaction.response.send_message("Ordered your lunch!", ephemeral=True)

        elif res == 0:  # No ID yet.
            button = Button(label="Lunch Order Website", url="https://lunch.jamesrumsey.com/",
                            style=nextcord.ButtonStyle.blurple)
            view = View()
            view.add_item(button)
            txt = (
                "\n"
                "This Discord account is not linked to a user in our system.\n"
                "Let's fix that:\n\n"
                f"1. Copy it to your Discord ID to your clipboard: `{uid}`\n"
                "2. Click the attatched button to go to the Lunch Order Website.\n"
                "3. Login with your JRTI google account, and then navigate to the student form tab.\n"
                "4. There should be a field labeled \"Discord\": paste your ID into that field, then click save\n"
                "5. ???\n"
                "6. Profit\n\n"
                "If you have no idea what you just read you should just contact and administrator to help you."
            )
            await interaction.response.send_message(txt, ephemeral=True, view=view)

        else:  # An error happened
            await interaction.response.send_message(f"Error: {res}", ephemeral=True)

    async def milk(interaction):
        view = View()

        async def white(interaction):
            await place_order(interaction, "White")
        button = Button(label="White", style=nextcord.ButtonStyle.blurple)
        button.callback = white
        view.add_item(button)

        async def choc(interaction):
            await place_order(interaction, "Chocolate")
        button = Button(label="Chocolate", style=nextcord.ButtonStyle.blurple)
        button.callback = choc
        view.add_item(button)

        await interaction.response.send_message("Milk?", ephemeral=True, view=view)

    button = Button(label="Order Lunch", style=nextcord.ButtonStyle.blurple)
    button.callback = milk

    view = View()
    view.add_item(button)

    await message.reply("Lunch call!", view=view)


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id: # Message is not from bot
        if message.content[0] == "!": # Message is a command
            if message.content == "!lunch":
                await order_lunch(message)

bot.run(config["token"])

