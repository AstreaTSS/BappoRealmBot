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