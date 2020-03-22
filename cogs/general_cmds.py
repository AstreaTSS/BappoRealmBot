from discord.ext import commands
import discord, re, datetime, os, aiohttp

class GeneralCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_paste(self, content):

        posters = {
            "api_dev_key": os.environ.get("PASTEBIN_KEY"), 
            "api_option": "paste", 
            "api_paste_code": content
        }
        url = "https://pastebin.com/api/api_post.php"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=posters) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    print(resp.status)
                    print(await resp.text())
                    return "ERROR, contact Sonic49."
    
    @commands.command()
    async def help(self, ctx):
        
        help_embed = discord.Embed(
            title = "To see the list of commands and how to use them, please use the below link:", 
            colour = discord.Colour(0x4a7de2), 
            description = "https://tinyurl.com/bapporealmbothelp"
        )
        help_embed.set_author(
            name="Bappo Realm Custom Bot", 
            icon_url="https://cdn.discordapp.com/avatars/618993974048194560/9533dc8ab73566f714731f17ed90d913.png?size=256"
        )

        await ctx.send(embed=help_embed)

    @commands.command()
    async def ping(self, ctx):
        current_time = datetime.datetime.utcnow().timestamp()
        mes_time = ctx.message.created_at.timestamp()

        ping_discord = round((self.bot.latency * 1000), 2)
        ping_personal = round((current_time - mes_time) * 1000, 2)

        await ctx.send(f"Pong! `{ping_discord}` ms from discord.\n`{ping_personal}` ms personally (not accurate)")

    @commands.command()
    async def check_stats(self, ctx, season):
        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            count = 0
            list_of_people = []

            for member in ctx.guild.members:
                if season_x_role in member.roles:
                    count += 1
                    list_of_people.append(f"{member.display_name} || {member.name}#{member.discriminator} || {member.id}")

            mes_of_people = f"```\nQuery about people in season {season}:\n"
            for name in list_of_people:
                mes_of_people += name + "\n"

            url = await self.post_paste(mes_of_people)

            stats_embed = discord.Embed(
                title = f"There are {count} people that have the Season {season} Badge.", 
                colour = discord.Colour(0x4a7de2), 
                description = f"List of members: {url}"
            )

            stats_embed.set_author(
                name="Bappo Realm Custom Bot", 
                icon_url="https://cdn.discordapp.com/avatars/618993974048194560/9533dc8ab73566f714731f17ed90d913.png?size=256"
            )

            await ctx.send(embed=stats_embed)

def setup(bot):
    bot.add_cog(GeneralCMDS(bot))