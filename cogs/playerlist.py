from discord.ext import commands
import discord, cogs.cmd_checks, re
import urllib.parse, aiohttp, os, datetime

class Playerlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def gamertag_handler(self, xuid):
        if xuid in self.bot.gamertags.keys():
            return self.bot.gamertags[xuid]

        headers = {
            "X-Authorization": os.environ.get("OPENXBL_KEY"),
            "Accept": "application/json",
            "Accept-Language": "en-US"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://xbl.io/api/v2/account/{xuid}") as r:
                resp_json = await r.json()
                if "code" in resp_json.keys():
                    return f"User with xuid {xuid}"
                else:
                    settings = {}
                    for setting in resp_json["profileUsers"][0]["settings"]:
                        settings[setting["id"]] = setting["value"]

                    gamertag = settings["Gamertag"]

                    self.bot.gamertags[xuid] = gamertag
                    return gamertag
    
    async def bappo_club_get(self):
        headers = {
            "X-Auth": os.environ.get("XAPI_KEY"),
            "Content-Type": "application/json",
            "Accept-Language": "en-US"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://xapi.us/v2/clubs/details/3379884873194657") as r:
                resp_json = await r.json()
                return resp_json["clubs"][0]["clubPresence"]

    @commands.command(aliases = ["player_list", "get_playerlist", "get_player_list"])
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    @commands.cooldown(1, 300, commands.BucketType.default)
    async def playerlist(self, ctx):
        await ctx.send("This will probably take a long time. Please be patient.")

        async with ctx.channel.typing():
            now = datetime.datetime.utcnow()
            day_delta = datetime.timedelta(days = 1)
            day_ago = now - day_delta

            online_list = []
            offline_list = []
            club_presence = await self.bappo_club_get()

            for member in club_presence:
                last_seen = datetime.datetime.strptime(member["lastSeenTimestamp"][:-2], "%Y-%m-%dT%H:%M:%S.%f")

                if last_seen > day_ago:
                    gamertag = await self.gamertag_handler(member["xuid"])
                    if member["lastSeenState"] == "InGame":
                        online_list.append(f"{gamertag}")
                    else:
                        time_format = last_seen.strftime("%x %X UTC")
                        offline_list.append(f"{gamertag}: last seen {time_format}")
                else:
                    break
        
        if online_list != []:
            online_str = "```\nPeople online right now:\n\n"
            online_str += "\n".join(online_list)
            await ctx.send(online_str + "\n```")

        if offline_list != []:
            offline_str = "```\nOther people on in the last 24 hours:\n\n"
            offline_str += "\n".join(offline_list)
            await ctx.send(offline_str + "\n```")

def setup(bot):
    bot.add_cog(Playerlist(bot))