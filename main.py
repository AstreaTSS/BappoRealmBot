import discord, datetime, os
from discord.ext import commands

bot = commands.Bot(command_prefix='!?')

def is_mod_or_up(ctx):
    mod_role = ctx.guild.get_role(596185228179931156)
    owner_role = ctx.guild.get_role(596185339018608641)
    second_owner = ctx.guild.get_role(641841757121675264)

    member_roles = ctx.author.roles

    if mod_role in member_roles or owner_role in member_roles or second_owner in member_roles:
        return True
    return False

def is_gatekeeper_or_up(ctx):
    if is_mod_or_up(ctx):
        return True

    gatekeeper = ctx.guild.get_role(641619621178245121)
    member_roles = ctx.author.roles

    if gatekeeper in member_roles:
        return True
    return False

@bot.command()
async def ping(ctx):
    current_time = datetime.datetime.utcnow().timestamp()
    mes_time = ctx.message.created_at.timestamp()

    ping_discord = round((bot.latency * 1000), 2)
    ping_personal = round((current_time - mes_time) * 1000, 2)

    await ctx.send(f"Pong! `{ping_discord}` ms from discord.\n`{ping_personal}` ms personally (not accurate)")

@bot.command()
async def say(ctx, *args):
    if type(args[0]) is discord.TextChannel:
        channel = args[0]
        await channel.send(" ".join(args[1:]))
        await ctx.message.delete()
    else:
        await channel.send(" ".join(args))
        await ctx.message.delete()

@bot.command()
async def check_stats(ctx, season):
    season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
    if season_x_role == None:
        await ctx.send("Invalid season number!")
    else:
        count = 0
        mes_of_people = "```\n"

        for member in ctx.guild.members:
            if season_x_role in member.roles:
                count += 1
                mes_of_people += (f"{member.display_name}\n")

        await ctx.send(f'There are {count} people that have the S{season} badge.')
        await ctx.author.send(mes_of_people + "```")

@bot.command()
@commands.check(is_mod_or_up)
async def season_add(ctx, season, message_id):
    ori_mess = None

    try:
        ori_mess = await ctx.guild.get_channel(596186025630498846).fetch_message(int(message_id))
    except discord.NotFound:
        await ctx.send("Invalid message ID!")
    ori_timestamp = ori_mess.created_at.timestamp()

    guild_members = ctx.guild.members

    season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
    if season_x_role == None:
        await ctx.send("Invalid season number!")
    else:
        season_x_vets = []

        for member in guild_members:
            if member.joined_at.timestamp() < ori_timestamp and not member.bot:
                season_x_vets.append(member)

        for vet in season_x_vets:
            await vet.add_roles(season_x_role)
            print("Added " + vet.display_name)

        await ctx.send("Done! Added " + str(len(season_x_vets)) + " members!")

@bot.command()
@commands.check(is_mod_or_up)
async def role_id(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if role == None:
        await ctx.send("Invalid role name!")
    else:
        await ctx.send(str(role.id))

@bot.group()
@commands.check(is_gatekeeper_or_up)
async def gk(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid gatekeeper command passed...')

@gk.command()
async def verify(ctx, member: discord.Member):
    to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')
    member_role = discord.utils.get(ctx.guild.roles, name='Member')

    if not to_be_verified in member.roles:
        await ctx.send("This user is already verified!")
    else:
        await member.remove_roles(to_be_verified)
        await member.add_roles(member_role)

        await ctx.send(f"{member.mention} was verified!")

@gk.command()
async def kick(ctx, member: discord.Member, *, reason):
    to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')
    if not to_be_verified in member.roles:
        await ctx.send("You can't kick this user! They don't have the To Be Verified role!")
    else:
        await member.kick(reason=f"By {ctx.author.display_name}: {reason}")

@gk.command()
async def ban(ctx, member: discord.Member, *, reason):
    to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')
    if not to_be_verified in member.roles:
        await ctx.send("You can't ban this user! They don't have the To Be Verified role!")
    else:
        await member.ban(reason=f"By {ctx.author.display_name}: {reason}")

bot.remove_command("help")
@bot.command()
async def help(ctx):

    embed = discord.Embed(colour=discord.Colour(0x4a90e2), description="A list of every command offered by this bot.")

    embed.set_author(name="Bappo Realm Custom Bot", icon_url="https://cdn.discordapp.com/avatars/618993974048194560/9533dc8ab73566f714731f17ed90d913.png")

    embed.add_field(name="Usable By Everyone", value="`help - Displays this.\nping - Pings the bot.\nsay <optional channel, message> - Makes the bot " +
    "say whatever you command it to. Can specify channel to send.\ncheck_stats <season> - Checks the stats for the season you give. Doesn't support the latest season.`")
    embed.add_field(name="Gatekeeper+ Commands", value="`gk verify <user> - Verifies the user mentioned.\ngk kick <user, reason> - Kicks the user " + 
    "mentioned if they aren't verified. A reason is needed, too.\ngk ban <user, reason> - Bans the user mentioned if they aren't verified. A reason is needed, too.`")
    embed.add_field(name="Mod+ Commands", value="`season_add <season, a message id> - Gives the S<season> role (which must exist beforehand) to everyone " +
    "who joined before <a message id> was created.\nrole_id <role name> - Gets the ID of <role name)>.`")

    await ctx.send(embed=embed)

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
            gatekeeper = discord.utils.get(member.guild.roles, name='Gatekeeper')

            verify_channel = discord.utils.get(member.guild.channels, name='verify')
            gamertags = discord.utils.get(member.guild.channels, name='gamertags')

            await verify_channel.send("Welcome to the Bappo Realm, " + member.mention + "!\n\nYou might have " +
            "noticed that there's not a lot of channels. Well, that's because you have to be verified. To be verified, " +
            "check out the questions below and answer them here. Also, make sure to put your gamertag in " + gamertags.mention + " so that we " +
            "know who you are in Minecraft.\nA " + gatekeeper.mention + " will review them and verify you.\n\n" +
            "```\nVerification Questions:\n\n1. In what ways did you manage to access the server (don't just say advertising, be more specific)?" +
            "\n\n2. Is this your first time taking part in a minecraft community (server, realm, etc), if not, how many past communities " + 
            "have you participated in?\n\n3. Have you ever had any experience in being helpful in a community, and if so, how?\n\n" +
            "4. How long have you been participating in communities?\n\n5. What are you looking for in joining this server?\n\n6. In your own " +
            "words, summarize rules 2 and 6 (If you don't understand what this means, explain rules 2 and 6 like you would if explaining it to " +
            "another person).\n```")

@bot.event
async def on_message(mes):
    if not mes.guild == None and not mes.author.bot:
        if mes.channel.id == 638566668372541441 or mes.channel.id == 631597319103578122:
            owner_role = mes.guild.get_role(596185339018608641)
            second_owner = mes.guild.get_role(641841757121675264)

            if not owner_role in mes.author.roles:
                if not second_owner in mes.author.roles:
                    await mes.delete()

        await bot.process_commands(mes)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    activity = discord.Activity(name = 'over Bappo\'s Realm', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)

async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            print(original)

            owner = await bot.application_info().owner
            ctx.send(f"{owner.mention}: {original}")
    elif isinstance(error, commands.ArgumentParsingError):
        await ctx.send(error)

bot.run(os.environ.get("MAIN_TOKEN"))