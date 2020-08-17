from discord.ext import commands
import discord, re, time, os
import aiohttp, json, datetime

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

class GeneralCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def pastebin_cache(self, season):
        current_time = datetime.datetime.utcnow()

        if season in self.bot.pastebins.keys():
            entry = self.bot.pastebins[season]

            four_hours = datetime.timedelta(hours=4)
            four_hours_ago = current_time - four_hours

            if entry["time"] > four_hours_ago:
                return entry

        return None

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

    @commands.command(aliases=["check_season", "season_stats"])
    async def check_stats(self, ctx, season):
        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            cache = await self.pastebin_cache(season)
            if cache != None:
                url = cache["url"]
                count = cache["count"]
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

                url = await self.post_paste(title, str_of_people)
                self.bot.pastebins[season] = {
                    "time": datetime.datetime.utcnow(),
                    "url": url,
                    "count": count
                }

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

    @commands.command()
    async def gamertag_from_xuid(self, ctx, xuid: int):
        if str(xuid) in self.bot.gamertags.keys():
            await ctx.send(f"Gamertag for `{xuid}`: {self.bot.gamertags[str(xuid)]}")
        else:
            async with AuthenticationManager(os.environ.get("XBOX_EMAIL"), os.environ.get("XBOX_PASSWORD")) as auth_mgr:
                async with XboxLiveClient(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid) as xb_client:
                    profile = await xb_client.profile.get_profile_by_xuid(xuid)

                    try:
                        resp_json = await profile.json()
                    except aiohttp.ContentTypeError:
                        await ctx.send(f"ERROR: Unable to find gamertag from XUID `{xuid}`! Make sure you have entered it in correctly.")
                        return

            if "code" in resp_json.keys():
                await ctx.send(f"ERROR: Unable to find gamertag from XUID `{xuid}`! Make sure you have entered it in correctly.")
            else:
                settings = {}
                for setting in resp_json["profileUsers"][0]["settings"]:
                    settings[setting["id"]] = setting["value"]
                    
                self.bot.gamertags[str(xuid)] = settings["Gamertag"]
                await ctx.send(f"Gamertag for `{xuid}`: {settings['Gamertag']}")

    @commands.command()
    async def xuid_from_gamertag(self, ctx, *, gamertag):
        if gamertag in self.bot.gamertags.values():
            xuid = next(e for e in self.bot.gamertags.keys() if self.bot.gamertags[e] == gamertag)
            await ctx.send(f"XUID of `{gamertag}`: `{xuid}`")
        else:
            async with AuthenticationManager(os.environ.get("XBOX_EMAIL"), os.environ.get("XBOX_PASSWORD")) as auth_mgr:
                async with XboxLiveClient(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid) as xb_client:
                    profile = await xb_client.profile.get_profile_by_gamertag(gamertag)

                    try:
                        resp_json = await profile.json()
                    except aiohttp.ContentTypeError:
                        await ctx.send(f"ERROR: Unable to find XUID from gamertag `{gamertag}`! Make sure you have entered it in correctly.")
                        return

            if "code" in resp_json.keys():
                await ctx.send(f"ERROR: Unable to find XUID from gamertag `{gamertag}`! Make sure you have entered it in correctly.")
            else:
                xuid = resp_json["profileUsers"][0]["id"]
                self.bot.gamertags[str(xuid)] = gamertag
                await ctx.send(f"XUID of `{gamertag}`: `{xuid}`")

def setup(bot):
    bot.add_cog(GeneralCMDS(bot))