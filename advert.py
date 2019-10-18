import discord, datetime, os
from discord.ext import commands

bot = commands.Bot(command_prefix='!?')

@bot.command()
async def ping(ctx):
    current_time = datetime.datetime.utcnow().timestamp()
    mes_time = ctx.message.created_at.timestamp()

    ping_discord = round((bot.latency * 1000), 2)
    ping_personal = round((current_time - mes_time) * 1000, 2)

    await ctx.send(f"Pong! `{ping_discord}` ms from discord.\n`{ping_personal}` ms personally (not accurate)")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    bot.remove_command("help")

    activity = discord.Activity(name = 'over Bappo\'s Realm', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)

def run():
    global bot

    bot.run(os.environ.get("TEST_TOKEN"))