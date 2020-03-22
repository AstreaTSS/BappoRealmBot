from discord.ext import commands
import discord, cogs.cmd_checks, re

class SayCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def say(self, ctx, *message):

        args = list(message)
        optional_channel = None
        files_sent = []

        if (re.search("[<#>]", args[0])):
            channel_id = re.sub("[<#>]", "", args[0])
            optional_channel = ctx.guild.get_channel(int(channel_id))
            
        if ctx.message.attachments is not None:
            for a_file in ctx.message.attachments:
                to_file = await a_file.to_file()
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

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def embed_say(self, ctx, *message):

        args = list(message)
        optional_channel = None
        optional_color = None
        
        if (re.search("<[@#][!&]?[0-9]+>", args[0])):
            channel_id = re.sub("[<#>]", "", args[0])
            optional_channel = ctx.guild.get_channel(int(channel_id))
            args.pop(0)
        
        temp_arg = args[0].replace("#", "")
        if (re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', temp_arg)):
            hex_color = int(args[0].replace("#", ""), 16)
            optional_color = discord.Color(hex_color)
            args.pop(0)

        say_embed = discord.Embed()
        say_embed.title = args[0]
        say_embed.description = (" ".join(args[1:]))

        if optional_color != None:
            say_embed.colour = optional_color

        if optional_channel != None:
            await optional_channel.send(embed = say_embed)
            await ctx.send(f"Done! Check out {optional_channel.mention}!")
        else:
            await ctx.send(embed = say_embed)

def setup(bot):
    bot.add_cog(SayCMDS(bot))