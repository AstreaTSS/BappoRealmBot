import discord, os, datetime
from discord.ext import commands

bot = commands.Bot(command_prefix='!?')

def is_mod_or_up(ctx):
    mod_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    owner_role = discord.utils.get(ctx.guild.roles, name='Owner')

    member_roles = ctx.author.roles

    if mod_role in member_roles or owner_role in member_roles:
        return True
    return False

@bot.command()
async def ping(ctx):
    ping = round((bot.latency * 1000), 2)

    await ctx.send(f"Pong! `{ping}` ms")

@bot.command()
@commands.check(is_mod_or_up)
async def season_add(ctx, season, message_id):
    ori_mess = await ctx.guild.get_channel(596186025630498846).fetch_message(int(message_id))
    ori_timestamp = ori_mess.created_at.timestamp()

    guild_members = ctx.guild.members

    season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season} Badge')

    season_x_vets = []

    for member in guild_members:
        if member.joined_at.timestamp() < ori_timestamp and not member.bot:
            season_x_vets.append(member)

    for vet in season_x_vets:
        await vet.add_roles(season_x_role)
        print("Added " + vet.display_name)

    await ctx.send("Done! Added " + str(len(season_x_vets)) + " members!")


@bot.event
async def on_member_join(member):

    if member.bot:
        pass

    current_time = datetime.datetime.utcnow().timestamp()

    if (current_time - member.created_at.timestamp()) <= 604800:
        try:
            await member.send("Your account is too young to join the Bappo Realm Discord server. Try "
            "again once your discord account is 7 days old.")
        except discord.Forbidden:
            print(member.display_name + " blocked DMs.")

        await member.kick(reason="Too young account to join Bappo")
    else:
        mod_role = discord.utils.get(member.guild.roles, name='Moderator')

        verify_channel = discord.utils.get(member.guild.channels, name='verify')
        await verify_channel.send("Welcome to the Bappo Realm, " + member.mention + "!\n\nYou might have " +
        "noticed that there's not a lot of channels. Well, that's because you have to be verified. To be verified, " +
        "wait for a " + mod_role.mention + " to come on and ask you some questions. Nothing big, of course.")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    bot.remove_command("help")

    activity = discord.Activity(name = 'over Bappo\'s Realm', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)

bot.run(os.environ.get("MAIN_TOKEN"))