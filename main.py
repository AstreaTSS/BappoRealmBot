import discord, os
from discord.ext import commands

bot = commands.Bot(command_prefix='!?')

to_be_verified_users = []
user_and_key = {}
rules_id = 596186061697450015

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.is_owner()
async def season_add(ctx):
    ori_mess = await ctx.guild.get_channel(596186025630498846).fetch_message(620241865324757003)
    ori_timestamp = ori_mess.created_at.timestamp()

    guild_members = ctx.guild.members

    season_4_role = discord.utils.get(ctx.guild.roles, name='S4 Badge')

    season_4_vets = []

    for member in guild_members:
        if member.joined_at.timestamp() < ori_timestamp and not member.bot:
            season_4_vets.append(member)

    for vet in season_4_vets:
        await vet.add_roles(season_4_role)
        print("Added " + vet.display_name)

    await ctx.send("Done!")
    print("\nDone! Added " + str(len(season_4_vets)) + " members!")


@bot.event
async def on_member_join(member):
    global to_be_verified_users

    # to_be_verified = discord.utils.get(member.guild.roles, name='To Be Verified')
    # await member.add_roles(to_be_verified)

    rules = discord.utils.get(member.guild.channels, name='rules')

    welcome_channel = discord.utils.get(member.guild.channels, name='welcome')
    await welcome_channel.send("Welcome to the Bappo Realm, " + member.mention + "!\n\nYou might have " +
    "noticed that there's not a lot of channels. Well, that's because you have to be verified. To be verified, " +
    "look in " + rules.mention + " and find a code. Once you have the code, enter the code into the reactions " +
    "at the bottom of rules and input the code like a keypad (don't go too fast). Once you enter the code, " +
    "wait a few seconds, and you should be in. If you mess up, press the repeat button.")

    to_be_verified_users.append(member.id)

@bot.event
async def on_member_remove(member):
    if member.id in user_and_key:
        del user_and_key[member.id]
    if member.id in to_be_verified_users:
        to_be_verified_users.remove(member.id)

@bot.event
async def on_raw_reaction_add(payload):
    global to_be_verified_users
    global rules_id
    global user_and_key

    if payload.user_id in to_be_verified_users and payload.channel_id == rules_id:
        user = bot.get_user(payload.user_id)
        rules = bot.get_channel(payload.channel_id)
        message = await rules.fetch_message(payload.message_id)

        emoji_name = payload.emoji.name.replace(u"\u20E3", "")

        if payload.user_id in user_and_key:
            user_and_key[payload.user_id] += emoji_name
        else:
            user_and_key[payload.user_id] = emoji_name

        if emoji_name == u"\U0001F501":
            user_and_key[payload.user_id] = ""

        # print(user_and_key[payload.user_id])

        if user_and_key[payload.user_id] == os.environ.get("KEY_CODE"):
            member = message.guild.get_member(payload.user_id)
            to_be_verified = discord.utils.get(member.guild.roles, name='To Be Verified')
            member_role = discord.utils.get(member.guild.roles, name='Member')

            await member.remove_roles(to_be_verified)
            await member.add_roles(member_role)
            del user_and_key[payload.user_id]
            to_be_verified_users.remove(payload.user_id)

    await message.remove_reaction(payload.emoji.name, user)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    activity = discord.Activity(name = 'over Bappo\'s Realm', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)

bot.run(os.environ.get("MAIN_TOKEN"))