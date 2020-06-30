from discord.ext import commands, tasks
import discord, cogs.cmd_checks, re, asyncio
import urllib.parse, aiohttp, os, datetime

class Playerlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.pltask = self.bot.loop.create_task(self.playerlist_loop())

    def cog_unload(self):
        self.bot.pltask.cancel()

    async def playerlist_loop(self):
        chan = self.bot.get_channel(724355887942074509) # playerlist channel
        list_cmd = self.bot.get_command("playerlist")

        mes = await chan.fetch_message(724364574538858647) # a message in #playerlist
        a_ctx = await self.bot.get_context(mes)
        
        await a_ctx.invoke(list_cmd, no_init_mes=True, limited=True)

        await asyncio.sleep(3600)

    async def gamertag_handler(self, xuid):
        if xuid in self.bot.gamertags.keys():
            return self.bot.gamertags[xuid]

        headers = {
            "X-Authorization": os.environ.get("OPENXBL_KEY"),
            "Accept": "application/json",
            "Accept-Language": "en-US"
        }

        xuid = str(xuid).replace("%27", "")

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://xbl.io/api/v2/account/{xuid}") as r:
                try:
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
                except aiohttp.client_exceptions.ContentTypeError:
                    return f"User with xuid {xuid}"
    
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
    async def playerlist(self, ctx, **kwargs):

        if not "no_init_mes" in kwargs.keys():
            if self.bot.gamertags == {}:
                await ctx.send("This will probably take a long time as the bot does not have a gamertag cache. Please be patient.")
            else:
                await ctx.send("This might take a bit. Please be patient.")

        async with ctx.channel.typing():
            now = datetime.datetime.utcnow()

            if not "limited" in kwargs.keys():
                time_delta = datetime.timedelta(days = 1)
            else:
                time_delta = datetime.timedelta(hours = 2)

            time_ago = now - time_delta

            online_list = []
            offline_list = []
            club_presence = await self.bappo_club_get()

            for member in club_presence:
                last_seen = datetime.datetime.strptime(member["lastSeenTimestamp"][:-2], "%Y-%m-%dT%H:%M:%S.%f")

                if last_seen > time_ago:
                    gamertag = await self.gamertag_handler(member["xuid"])
                    if member["lastSeenState"] == "InGame":
                        online_list.append(f"{gamertag}")
                    else:
                        time_format = last_seen.strftime("%x %X (%I:%M:%S %p) UTC")
                        offline_list.append(f"{gamertag}: last seen {time_format}")
                else:
                    break
        
        if online_list != []:
            online_str = "```\nPeople online right now:\n\n"
            online_str += "\n".join(online_list)
            await ctx.send(online_str + "\n```")

        if offline_list != []:
            if len(offline_list) < 20:
                if not "limited" in kwargs.keys():
                    offline_str = "```\nOther people on in the last 24 hours:\n\n"
                else:
                    offline_str = "```\nOther people on in the last 2 hours:\n\n"

                offline_str += "\n".join(offline_list)
                await ctx.send(offline_str + "\n```")
            else:
                chunks = [offline_list[x:x+20] for x in range(0, len(offline_list), 20)]

                if not "limited" in kwargs.keys():
                    first_offline_str = "```\nOther people on in the last 24 hours:\n\n" + "\n".join(chunks[0]) + "\n```"
                else:
                    first_offline_str = "```\nOther people on in the last 2 hours:\n\n" + "\n".join(chunks[0]) + "\n```"
                    
                await ctx.send(first_offline_str)

                for x in range(len(chunks)):
                    if x == 0:
                        continue
                    
                    offline_chunk_str = "```\n" + "\n".join(chunks[x]) + "\n```"
                    await ctx.send(offline_chunk_str)

def setup(bot):
    bot.add_cog(Playerlist(bot))