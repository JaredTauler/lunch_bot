from .database import Database, Guild
import types

from nextcord.ext import commands
from __main__ import CONFIG
from .order import LunchOrder

from nextcord.ext import tasks
from nextcord.ui import Button, View
import nextcord
import datetime as dt
import asyncio
import time
from .menu import LunchMenu

from nextcord.ext import commands


# Update status to reflect how many users have ordered lunch while avoiding getting rate limited.
class CountStatus():
    def __init__(self, bot):
        self.count = 0
        self.order = []
        self.last = dt.datetime.now()
        self.bot = bot

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
                    await self.bot.change_presence(
                        activity=nextcord.Game(name=f"{self.count} ordered today!")
                    )
                    self.last = self.order[0]
                    self.order.pop(0)

        asyncio.create_task(func())  # "Fire and forget"

#Handle command errors + give thumbs up
def CommandCatch(func):
    async def wrapper(self, *args):
        ctx = args[0]
        try:
            # *args could be passed as well.
            if (await func(self, ctx)):  # Commands return True if don't need a thumbs up.
                return
        except Exception as e:
            await ctx.reply(f"Error: {e}")
        else:
            await ctx.message.reply(":thumbsup:")

    wrapper.__name__ = func.__name__  # discord.py binds __name__ to commands.
    return wrapper


class NewCog(commands.Cog, name="Lunch Order"):
    def __init__(self, bot: commands.Bot):
        self.__bot = bot

        self.Session = Database(CONFIG["db-string"]).Session
        self.Announce_Lunch.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.Count = CountStatus(self.__bot)
        self.__bot.add_view(LunchOrder(self.Count)) # Load on ready


    def this_server(self, session, ctx):
        guild_id = str(ctx.message.guild.id)

        def func():
            return session.query(Guild).filter(Guild.id == guild_id).first()

        this = func()
        if this is None:  # Make new row if doesnt exist
            new = Guild(id=guild_id)
            session.add(new)
            session.commit()
            this = func()  # Try getting again
        return this

    @commands.has_permissions(administrator=True)
    @commands.command()
    @CommandCatch
    async def set_role(self, ctx):
        role = str(ctx.message.raw_role_mentions[0])
        print(role)
        with self.Session() as session:
            row = self.this_server(session, ctx)
            if len(role) == 0:
                row.ping_role = None
            else:
                row.ping_role = role
            session.commit()

    # Set channel to send lunch texts
    @commands.has_permissions(administrator=True)
    @commands.command()
    @CommandCatch
    async def here(self, ctx):
        with self.Session() as session:
            row = self.this_server(session, ctx)
            row.announce_channel = str(ctx.message.channel.id)
            session.commit()

    # Give user role
    @commands.command()
    @CommandCatch
    async def pingme(self, ctx):
        with self.Session() as session:
            row = self.this_server(session, ctx)
            if row.ping_role is None:
                await ctx.message.reply("An administrator needs to set the ping role using `!set_role @role`")
                return
            role = ctx.guild.get_role(int(row.ping_role))
            author = ctx.author

            if role.id in [int(i.id) for i in author.roles]:  # Check if ping role is on user
                await author.remove_roles(role)
                await ctx.message.reply(":no_bell:")
                return True
            else:
                await author.add_roles(role)
                await ctx.message.reply(":bell:")
                return True

    @commands.has_permissions(administrator=True)
    @commands.command()
    # @CommandCatch
    async def test(self, ctx):
        # from cogs.lunch_order.oldmain import Announce_Lunch  # Yes this needs to be down here.
        with self.Session() as session:
            row = self.this_server(session, ctx)

        await self.Announce_Lunch(
            [[row.announce_channel, row.ping_role]]
        )

    ## Order loop
    @tasks.loop(hours=24)  # Every 24 hours
    async def Announce_Lunch(self, ChannelList=None):

        menu = LunchMenu.Today()

        if not menu:
            for i in ChannelList:
                channel = self.__bot.get_channel(int(i[0]))
                await channel.send("No lunch today :frowning2:")
            return

        if not ChannelList:  # Test mode if not ChannelList, Lunch is being ordered if menu is true
            with self.Session() as session:
                ChannelList = session.query(Guild.announce_channel, Guild.ping_role).all()

        # view = main().orderview()

        def role():
            if i[1] != None:
                return f"<@&{str(i[1])}>"
            else:
                return ""

        def is_me(m):
            return m.author == self.__bot.user

        # For every channel
        for i in ChannelList:
            try:
                channel = self.__bot.get_channel(int(i[0]))
                await channel.send(
                    f"{role()} Who wants lunch?\n{menu[0]}",
                    view=LunchOrder(self.Count),
                    file=menu[1]
                )
            except Exception as e:
                print(
                    f"Couldnt send message: {e}"
                )
            try:
                for member in channel.guild.members: # all members in server.
                    if i[1] in [str(i.id) for i in member.roles]: # if ping role belongs to member
                        dm = await member.create_dm()
                        await dm.send(
                            f"Do you want lunch?\n{menu[0]}",
                            view=LunchOrder(self.Count),
                            file=menu[1]
                        )
            except Exception as e:
                print(
                    f"Couldnt send message: {e}"
                )


    @Announce_Lunch.before_loop
    async def before_my_task(self):

        hour = int(CONFIG["announce_time"]["hour"])
        minute = int(CONFIG["announce_time"]["minute"])

        # await self.__bot.wait_until_ready()

        now = dt.datetime.now()
        future = dt.datetime(now.year, now.month, now.day, hour, minute)  # Current time but with new hour and minute

        if now.hour >= hour and now.minute > minute:  # If time has passed add 24 hours
            future += dt.timedelta(hours=24)
        await asyncio.sleep(
            (future - now).seconds
        )  # Wait the difference in seconds of current time and time to start.


def setup(bot):
    bot.add_cog(NewCog(bot))
