# Jared Tauler
from __main__ import bot, CONFIG, ON_READY, DB as Session
from nextcord.ext import commands
import lunch_order.database as db

def this_server(session, ctx):
    guild_id = str(ctx.message.guild.id)
    def func():
        return session.query(db.Guild).filter(db.Guild.id == guild_id).first()
    this = func()
    if this is None: # Make new row if doesnt exist
        new = db.Guild(id = guild_id)
        session.add(new)
        session.commit()
        this = func() # Try getting again
    return this

# Handle command errors + give thumbs up
def CommandCatch(func):
    async def wrapper(*args):
        ctx = args[0]
        try:
            # *args could be passed as well.
            if (await func(ctx)): # Commands return True if don't need a thumbs up.
                return
        except Exception as e:
            await ctx.reply(f"Error: {e}")
        else:
            await ctx.message.reply(":thumbsup:")
    wrapper.__name__ = func.__name__  # discord.py binds __name__ to commands.
    return wrapper

@commands.has_permissions(administrator=True)
@bot.command()
@CommandCatch
async def set_role(ctx):
    role = str(ctx.message.raw_role_mentions[0])
    print(role)
    with Session() as session:
        row = this_server(session, ctx)
        if len(role) == 0:
            row.ping_role = None
        else:
            row.ping_role = role
        session.commit()

# Set channel to send lunch texts
@commands.has_permissions(administrator=True)
@bot.command()
@CommandCatch
async def here(ctx):
    with Session() as session:
        row = this_server(session, ctx)
        row.announce_channel = str(ctx.message.channel.id)
        session.commit()

# Give user role
@bot.command()
@CommandCatch
async def pingme(ctx):
    with Session() as session:
        row = this_server(session, ctx)
        if row.ping_role is None:
            await ctx.message.reply("An administrator needs to set the ping role using `!set_role @role`")
            return
        role = ctx.guild.get_role(int(row.ping_role))
        author = ctx.author

        if role.id in [int(i.id) for i in author.roles]: # Check if ping role is on user
            await author.remove_roles(role)
            await ctx.message.reply(":no_bell:")
            return True
        else:
            await author.add_roles(role)
            await ctx.message.reply(":bell:")
            return True

@commands.has_permissions(administrator=True)
@bot.command()
# @CommandCatch
async def test(ctx):
    from lunch_order.main import Announce_Lunch # Yes this needs to be down here.
    with Session() as session:
        row = this_server(session, ctx)

    await Announce_Lunch(
        [[row.announce_channel, row.ping_role]]
    )
