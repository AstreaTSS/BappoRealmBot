import traceback

def is_mod_or_up(ctx):
    mod_role = ctx.guild.get_role(596185228179931156)
    owner_role = ctx.guild.get_role(596185339018608641)
    second_owner = ctx.guild.get_role(641841757121675264)

    member_roles = ctx.author.roles

    if mod_role in member_roles or owner_role in member_roles:
        return True
    elif second_owner in member_roles:
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

async def error_handle(bot, error, ctx = None):
    # handles errors and sends them to owner
    error_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))

    await msg_to_owner(bot, error_str)

    if ctx != None:
        await ctx.send("An internal error has occured. The bot owner has been notified.")

async def msg_to_owner(bot, content):
    # sends a message to the owner
    owner = bot.owner
    string = str(content)

    str_chunks = [string[i:i+1950] for i in range(0, len(string), 1950)]

    for chunk in str_chunks:
        await owner.send(f"{chunk}")