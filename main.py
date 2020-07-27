import discord, os, humanize
import logging, datetime
from discord.ext import commands
import cogs.utils as utils

log = logging.getLogger('authentication')
log.setLevel(logging.ERROR)

bot = commands.Bot(command_prefix='!?', fetch_offline_members=True, case_insensitive=True)
bot.remove_command("help")

@bot.event
async def on_ready():

    if bot.init_load == True:
        bot.gamertags = {}
        bot.pastebins = {}
        
        application = await bot.application_info()
        bot.owner = application.owner

        cogs_list = ("cogs.events.countdown", "cogs.events.etc", "cogs.cmds.general_cmds", "cogs.events.kick_unverified",
        "cogs.cmds.mod_cmds", "cogs.events.remove_warnings", "cogs.cmds.say_cmds", "cogs.cmds.playerlist", 
        "cogs.eval_cmd", "cogs.cmds.slow_playerlist")

        for cog in cogs_list:
            bot.load_extension(cog)

        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------\n')

        activity = discord.Activity(name = 'over the Bappo Realm', type = discord.ActivityType.watching)
        await bot.change_presence(activity = activity)

    utcnow = datetime.datetime.utcnow()
    time_format = utcnow.strftime("%x %X UTC")

    connect_str = "Connected" if bot.init_load else "Reconnected"

    await utils.msg_to_owner(bot, f"{connect_str} at `{time_format}`!")

    bot.init_load = False
    
@bot.check
async def block_dms(ctx):
    if ctx.invoked_with == "dm_say":
        return ctx.guild is None
    else:
        return ctx.guild is not None

@bot.event
async def on_error(event, *args, **kwargs):
    try:
        raise
    except Exception as e:
        await utils.error_handle(bot, e)

async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            await utils.error_handle(bot, error, ctx)
    elif isinstance(error, (commands.ConversionError, commands.UserInputError)):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        if ctx.guild != None:
            await ctx.send("You do not have the proper permissions to use that command.")
    elif isinstance(error, commands.CommandOnCooldown):
        delta_wait = datetime.timedelta(seconds=error.retry_after)
        await ctx.send(f"You're doing that command too fast! Try again in {humanize.precisedelta(delta_wait, format='%0.0')}.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await utils.error_handle(bot, error, ctx)

bot.init_load = True
bot.run(os.environ.get("MAIN_TOKEN"))
