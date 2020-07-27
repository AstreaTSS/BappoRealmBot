from discord.ext import commands
import discord, cogs.utils, asyncio
import urllib.parse, aiohttp, os, datetime

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

class Playerlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_diff_xuids(self, users, list_xuids, new_list_xuids):
        for xuid in list_xuids:
            if xuid not in new_list_xuids:
                index = list_xuids.index(xuid)
                users.insert(index, "Gamertag not gotten")

        return users

    async def try_until_valid(self, xb_client, list_xuids):
        profiles = await xb_client.profile.get_profiles(list_xuids)
        profiles = await profiles.json()

        if "code" in profiles.keys():
            description = profiles["description"]
            desc_split = description.split(" ")
            list_xuids.remove(desc_split[1])

            profiles, list_xuids = await self.try_until_valid(xb_client, list_xuids)
            return profiles, list_xuids

        elif "limitType" in profiles.keys():
            await asyncio.sleep(15)
            profiles, list_xuids = await self.try_until_valid(xb_client, list_xuids)
            return profiles, list_xuids

        return profiles, list_xuids
    
    async def bappo_club_get(self, xb_client):
        club = await xb_client.clubs.get_club_user_presence(3379884873194657)
        resp_json = await club.json()
        return resp_json["clubs"][0]["clubPresence"]

    @commands.command(aliases = ["player_list", "get_playerlist", "get_player_list"])
    @commands.check(cogs.utils.is_mod_or_up)
    @commands.cooldown(1, 60, commands.BucketType.default)
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

            xuid_list = []
            state_list = []
            last_seen_list = []

            online_list = []
            offline_list = []

            async with AuthenticationManager(os.environ.get("XBOX_EMAIL"), os.environ.get("XBOX_PASSWORD")) as auth_mgr:
                async with XboxLiveClient(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid) as xb_client:
                    club_presence = await self.bappo_club_get(xb_client)

                    for member in club_presence:
                        last_seen = datetime.datetime.strptime(member["lastSeenTimestamp"][:-2], "%Y-%m-%dT%H:%M:%S.%f")
                        if last_seen > time_ago:
                            xuid_list.append(member["xuid"])
                            state_list.append(member["lastSeenState"])
                            last_seen_list.append(last_seen)
                        else:
                            break

                    xuid_list_filter = xuid_list.copy()
                    for xuid in xuid_list_filter:
                        if str(xuid) in self.bot.gamertags.keys():
                            xuid_list_filter.remove(xuid)

                    profiles, new_xuid_list = await self.try_until_valid(xb_client, xuid_list_filter)
                    users = profiles["profileUsers"]
                    users = self.get_diff_xuids(users, xuid_list, new_xuid_list)

            def add_list(gamertag, state, last_seen):
                if state == "InGame":
                    online_list.append(f"{gamertag}")
                else:
                    time_format = last_seen.strftime("%x %X (%I:%M:%S %p) UTC")
                    offline_list.append(f"{gamertag}: last seen {time_format}")

            for i in range(len(xuid_list)):
                entry = users[i]
                state = state_list[i]
                last_seen = last_seen_list[i]

                gamertag = f"User with xuid {xuid_list[i]}"

                if entry == "Gamertag not gotten":
                    if str(xuid_list[i]) in self.bot.gamertags.keys():
                        gamertag = self.bot.gamertags[str(xuid_list[i])]
                else:
                    try:
                        settings = {}
                        for setting in entry["settings"]:
                            settings[setting["id"]] = setting["value"]

                        gamertag = settings["Gamertag"]
                        self.bot.gamertags[str(xuid_list[i])] = gamertag
                    except KeyError:
                        gamertag = f"User with xuid {xuid_list[i]}"

                add_list(gamertag, state, last_seen)
        
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