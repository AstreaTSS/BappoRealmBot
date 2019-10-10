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
    current_time = datetime.datetime.utcnow().timestamp()
    mes_time = ctx.message.created_at

    ping_discord = round((bot.latency * 1000), 2)
    ping_personal = round((current_time - mes_time) * 1000, 2)

    await ctx.send(f"Pong! `{ping_discord}` ms from discord.\n{ping_personal} ms personally (not accurate)")

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

    if not member.bot:
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
            "check out the questions below and answer them. A " + mod_role.mention + " will review them and verify you.\n\n" +
            "```\nVerification Questions:\n\n1. In what ways did you manage to access the server (via advertising links, friends, etc)?" +
            "\n\n2. Is this your first time taking part in a minecraft community (server, realm, etc), if not, how many past communities " + 
            "have you participated in?\n\n3. Have you ever had any experience in being helpful in a community, and if so, how?\n\n" +
            "4. How long have you been participating in communities?\n\n5. What are you looking for in joining this server?\n```")

@bot.event
async def on_message(mes):
    if mes.channel.id == 631597319103578122 or mes.channel.id == 631327297278050348:
        owner_role = discord.utils.get(mes.guild.roles, name='Owner')

        if not owner_role in mes.author.roles:
            mes.delete()

    await bot.process_commands(mes)

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