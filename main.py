import discord, os, traceback
from discord.ext import commands
from datetime import datetime

bot = commands.Bot(command_prefix='!?', fetch_offline_members=True)

bot.remove_command("help")

async def error_handle(bot, error, ctx = None):
    error_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
    await msg_to_owner(bot, error_str)

    if ctx != None:
        await ctx.send("An internal error has occured. The owner of the bot has been notified.")

async def msg_to_owner(bot, string):
    application = await bot.application_info()
    owner = application.owner
    await owner.send(f"{string}")

@bot.event
async def on_ready():

    if bot.init_load == True:
        bot.gamertags = {}

        cogs_list = ["cogs.events.countdown", "cogs.events.etc", "cogs.cmds.general_cmds", "cogs.events.kick_unverified",
        "cogs.cmds.mod_cmds", "cogs.events.remove_warnings", "cogs.cmds.say_cmds", "cogs.cmds.playerlist", 
        "cogs.eval_cmd"]

        for cog in cogs_list:
            bot.load_extension(cog)

        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------\n')

        activity = discord.Activity(name = 'over the Bappo Realm', type = discord.ActivityType.watching)
        await bot.change_presence(activity = activity)
    else:
        utcnow = datetime.utcnow()
        time_format = utcnow.strftime("%x %X UTC")

        await msg_to_owner(bot, f"Reconnected at {time_format}!")

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
        await error_handle(bot, e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            await error_handle(bot, error, ctx)
    elif isinstance(error, (commands.ConversionError, commands.UserInputError, commands.CommandOnCooldown)):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        if ctx.guild != None:
            await ctx.send("You do not have the proper permissions to use that command.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await error_handle(bot, error, ctx)

bot.init_load = True
bot.run(os.environ.get("MAIN_TOKEN"))
