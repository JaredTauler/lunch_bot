# Jared Tauler

from __main__ import bot, CONFIG, ON_READY, DB as Session

import cogs.lunch_order.database as db

from cogs.lunch_order.menu import LunchMenu

# Anvil
from cogs.lunch_order.anvil_wrapper import lunch_to_server, auth as anvil_auth
anvil_auth(CONFIG["anvil-token"])

# Discord
from nextcord.ui import Button, View
import nextcord
from nextcord.ext import tasks

# Misc
import datetime as dt
import asyncio
import time

# Update status to reflect how many users have ordered lunch while avoiding getting rate limited.
class CountStatus():
    def __init__(self):
        self.count = 0
        self.order = []
        self.last = dt.datetime.now()

    def another(self):
        async def func():
            self.order.append(dt.datetime.now())
            if len(self.order) > 1:  # An instance of this function is already running
                return
            else:
                while self.order != []:
                    # Sleep 10 seconds if last order was less than 10 seconds ago
                    if (self.order[0] - self.last).seconds < 10:
                        time.sleep(10)
                    self.count += 1
                    await bot.change_presence(
                        activity=nextcord.Game(name=f"{self.count} ordered today!")
                    )
                    self.last = self.order[0]
                    self.order.pop(0)

        asyncio.create_task(func())  # "Fire and forget"
Count = CountStatus()

## Order loop
@tasks.loop(hours=24) # Every 24 hours
async def Announce_Lunch(ChannelList=None):
    menu = LunchMenu.Today()

    if not menu:
        for i in ChannelList:
            channel = bot.get_channel(int(i[0]))
            await channel.send("No lunch today :frowning2:")
        return

    if not ChannelList: # Test mode if not ChannelList, Lunch is being ordered if menu is true
        with Session() as session:
            ChannelList = session.query(db.Guild.announce_channel, db.Guild.ping_role).all()

    view = order_lunch()
    def role():
        if i[1] != None:
            return f"<@&{str(i[1])}> "
        else:
            return ""

    def is_me(m):
        return m.author == bot.user

    # For every channel
    for i in ChannelList:
        try:
            channel = bot.get_channel(int(i[0]))
            await channel.send(
                f"{role()}Who wants lunch?\n{menu[0]}",
                view=view,
                file=menu[1]
            )
        except Exception as e:
            print(
                f"Couldnt send message: {e}"
            )

@Announce_Lunch.before_loop
async def before_my_task():
    hour = int(CONFIG["announce_time"]["hour"])
    minute = int(CONFIG["announce_time"]["minute"])

    await bot.wait_until_ready()

    now = dt.datetime.now()
    future = dt.datetime(now.year, now.month, now.day, hour, minute) # Current time but with new hour and minute

    if now.hour >= hour and now.minute > minute: # If time has passed add 24 hours
        future += dt.timedelta(hours=24)

    await asyncio.sleep((future-now).seconds) # Wait the difference in seconds of current time and time to start.

ON_READY.append(Announce_Lunch)

# Lunch ordering routine
# This just returns the view so this can be used in different places.
async def order_lunch():
    async def place_order(interaction, milk):
        uid = interaction.user.id
        res = lunch_to_server(uid, milk)  # Make API call.

        if res == 1:  # Success
            await interaction.response.send_message("Ordered your lunch!", ephemeral=True)
            Count.another() # Update status.

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

    # There is a more dynamic way to pick an option. But there will only ever be two choices, so dont care.
    async def milk(interaction):
        def white(view):
            async def click(interaction):
                await place_order(interaction, "White")
            button = Button(label="White", style=nextcord.ButtonStyle.blurple)
            button.callback = click
            view.add_item(button)
        def choc(view):
            async def click(interaction):
                await place_order(interaction, "Chocolate")
            button = Button(label="Chocolate", style=nextcord.ButtonStyle.blurple)
            button.callback = click
            view.add_item(button)

        view = View()
        white(view)
        choc(view)

        await interaction.response.send_message("Milk?", ephemeral=True, view=view)

    button = Button(label="Order Lunch", style=nextcord.ButtonStyle.blurple)
    button.callback = milk

    view = View()
    view.add_item(button)

    return view
#
# while True:
#         previous_page = current
#         moderatorI = await bot.wait_for("button_click")
