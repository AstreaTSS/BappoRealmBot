import discord, os
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
async def globally_block_dms(ctx):
    return ctx.guild is not None

async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            print(original)

            owner = await bot.application_info().owner
            await ctx.send(f"{owner.mention}: {original}")
    elif isinstance(error, commands.ArgumentParsingError):
        await ctx.send(error)
    else:
        print(error)
        owner = await bot.application_info().owner
        await ctx.send(f"{owner.mention}: {error}")

bot.run(os.environ.get("MAIN_TOKEN"))
