import discord, os
import keep_alive
from discord.ext import commands

bot = commands.Bot(command_prefix='!?', fetch_offline_members=True)

bot.remove_command("help")

@bot.event
async def on_ready():

    cogs_list = ["cogs.countdown", "cogs.etc", "cogs.general_cmds", "cogs.kick_unverified",
    "cogs.mod_cmds", "cogs.remove_warnings", "cogs.say_cmds"]

    for cog in cogs_list:
        bot.load_extension(cog)

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    activity = discord.Activity(name = 'over the Bappo Realm', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)
    
@bot.check
async def block_dms(ctx):
    if ctx.invoked_with == "dm_say":
        return ctx.guild is None
    else:
        return ctx.guild is not None

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            print(original)

            application = await ctx.bot.application_info()
            owner = application.owner
            await ctx.send(f"{owner.mention}: {original}")
    elif isinstance(error, (commands.ConversionError, commands.UserInputError)):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        dms_check = await block_dms(ctx)
        if not dms_check:
            await ctx.send("You do not have the proper permissions to use that command.")
    elif isinstance(error, commands.CommandNotFound):
        ignore = True
    else:
        print(error.original)
        
        application = await ctx.bot.application_info()
        owner = application.owner
        await ctx.send(f"{owner.mention}: {error.original}")

keep_alive.keep_alive()

bot.run(os.environ.get("MAIN_TOKEN"))
