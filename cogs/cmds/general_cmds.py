from discord.ext import commands
import discord, re, time, os
import aiohttp, json, datetime

class GeneralCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def pastebin_cache(self, season, title, content):
        current_time = datetime.datetime.utcnow()

        if season in self.bot.pastebins.keys():
            entry = self.bot.pastebins[season]

            four_hours = datetime.timedelta(hours=4)
            four_hours_ago = current_time - four_hours

            if entry["time"] > four_hours_ago:
                return entry["url"]
        
        url = self.post_paste(time, content)
        self.bot.pastebins[season] = {
            "url": url,
            "time": current_time
        }

        return url

    async def post_paste(self, title, content):
        headers = {
            "Authorization": f"Token {os.environ.get('GLOT_KEY')}",
            "Content-type": "application/json",
        }
        data = {
            "language": "plaintext",
            "title": f"{title}",
            "public": False,
            "files": [
                {
                    "name": "main.txt",
                    "content": f"{content}"
                }
            ]
        }
        url = "https://snippets.glot.io/snippets"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
                if resp.status == 200:
                    resp_json = await resp.json()
                    snippet_id = resp_json["id"]
                    return f"https://glot.io/snippets/{snippet_id}"
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
        start_time = time.perf_counter()
        ping_discord = round((self.bot.latency * 1000), 2)

        mes = await ctx.send(f"Pong!\n`{ping_discord}` ms from Discord.\nCalculating personal ping...")
        
        end_time = time.perf_counter()
        ping_personal = round(((end_time - start_time) * 1000), 2)
        
        await mes.edit(content=f"Pong!\n`{ping_discord}` ms from Discord.\n`{ping_personal}` ms personally.")

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

            title = f"Query about people in Season {season}"
            str_of_people = ""
            for name in list_of_people:
                str_of_people += name + "\n"

            url = await self.pastebin_cache(season, title, str_of_people)

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