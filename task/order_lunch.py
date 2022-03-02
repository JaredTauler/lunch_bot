from __main__ import bot, CONFIG, READY

import database as db

# Anvil
from anvil_wrapper import lunch_to_server, auth as anvil_auth
anvil_auth(CONFIG["anvil-token"])

# Discord
from nextcord.ui import Button, View, Select
import nextcord
from nextcord.ext import tasks, commands

# Misc
import datetime as dt
import asyncio


# @Announce_Lunch.before_loop
# async def before_my_task():
#     hour = 9
#     minute = 30
#     await bot.wait_until_ready()
#     now = dt.datetime.now()
#     future = dt.datetime(now.year, now.month, now.day, hour, minute)
#     if now.hour >= hour and now.minute > minute:
#         future += dt.timedelta(seconds=5)
#     await asyncio.sleep((future-now).seconds)

@tasks.loop(hours=24) # Every day
async def Announce_Lunch():
    with db.Session() as session:
        ChannelList = session.query(db.Guild.announce_channel).all()

    view = order_lunch()
    message = "Lunch call"

    for i in ChannelList:
        try:
            channel = bot.get_channel(int(i[0]))
            await channel.send("Who wants lunch?", view=view)
        except Exception as e:
            print(
                f"Couldnt send message: {e}"
            )

READY.append(Announce_Lunch)

@commands.has_permissions(administrator=True)
@bot.command()
async def LunchHere(str):
    print(str)
def order_lunch():
    async def place_order(interaction, milk):
        uid = interaction.user.id
        res = lunch_to_server(uid, milk)  # Make API call.

        if res == 1:  # Success
            await interaction.response.send_message("Ordered your lunch!", ephemeral=True)

        elif res == 0:  # No ID yet.
            button = Button(label="Connect Discord with JRTI Lunch", url="https://lunch.jamesrumsey.com/#discord",
                            style=nextcord.ButtonStyle.blurple)
            view = View()
            view.add_item(button)
            txt = (
                ":face_with_raised_eyebrow:\n"
                "This Discord account is not linked to a user in our system.\n"
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

    return view
