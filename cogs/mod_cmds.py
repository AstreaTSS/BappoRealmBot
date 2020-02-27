from discord.ext import commands
import discord, cogs.cmd_checks, re

class ModCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def season_add(self, ctx, season, message_id):
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

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def role_id(self, ctx, *role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if role == None:
            await ctx.send("Invalid role name!")
        else:
            await ctx.send(str(role.id))

    @commands.command()
    @commands.check(cogs.cmd_checks.is_gatekeeper_or_up)
    async def verify(self, ctx, member: discord.Member):
        to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')
        member_role = discord.utils.get(ctx.guild.roles, name='Member')

        if not to_be_verified in member.roles:
            await ctx.send("This user is already verified!")
        else:
            await member.remove_roles(to_be_verified)
            await member.add_roles(member_role)

            await ctx.send(f"{member.mention} was verified!")

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def say(self, ctx, *, message):

        args = message.split(" ")

        optional_channel = None
        files_sent = []

        if (re.search("[<#>]", args[0])):
            channel_id = re.sub("[<#>]", "", args[0])
            optional_channel = ctx.guild.get_channel(int(channel_id))
            
        if ctx.message.attachments is not None:
            for file in attachment:
                to_file = await file.to_file()
                files_sent.append(to_file)
                
        if files == []:
            if optional_channel is not None:
                await optional_channel.send(" ".join(args[1:]))
            else:
                await ctx.send(" ".join(args))
        else:
            if optional_channel is not None:
                await optional_channel.send(content=" ".join(args[1:]), files=files_sent)
            else:
                await ctx.send(content=" ".join(args), files=files_sent)

def setup(bot):
    bot.add_cog(ModCMDS(bot))
