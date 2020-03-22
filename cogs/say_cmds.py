from discord.ext import commands
import discord, cogs.cmd_checks, re

class SayCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            for file in ctx.message.attachments:
                to_file = await file.to_file()
                files_sent.append(to_file)
                
        if files_sent == []:
            if optional_channel is not None:
                await optional_channel.send(" ".join(args[1:]))
                await ctx.send(f"Done! Check out {optional_channel.mention}!")
            else:
                await ctx.send(" ".join(args))
        else:
            if optional_channel is not None:
                await optional_channel.send(content=" ".join(args[1:]), files=files_sent)
                await ctx.send(f"Done! Check out {optional_channel.mention}!")
            else:
                await ctx.send(content=" ".join(args), files=files_sent)

def setup(bot):
    bot.add_cog(SayCMDS(bot))