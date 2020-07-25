from discord.ext import commands
import discord, cogs.cmd_checks, re, asyncio
import urllib.parse, aiohttp, os, collections

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

class ModCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def auth_mgr_create(self):
        auth_mgr = await AuthenticationManager.create()
        auth_mgr.email_address = os.environ.get("XBOX_EMAIL")
        auth_mgr.password = os.environ.get("XBOX_PASSWORD")
        await auth_mgr.authenticate()
        await auth_mgr.close()

        return auth_mgr

    async def xbl_handler(self, gamertag, user):
        auth_mgr = await self.auth_mgr_create()

        mem_gt_url = gamertag

        client = await XboxLiveClient.create(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid)
        profile = await client.profile.get_profile_by_gamertag(mem_gt_url)
        await client.close()

        resp_json = await profile.json()
        if "code" in resp_json.keys():
            return f"ERROR: Unable to find {user.mention}'s gamertag, `{gamertag}`!"
        else:
            settings = {}
            for setting in resp_json["profileUsers"][0]["settings"]:
                settings[setting["id"]] = setting["value"]
            
            if settings["XboxOneRep"] != "GoodPlayer":
                return "".join((f"WARNING: {user.mention}'s gamertag exists, but doesn't have the best reputation on Xbox Live! ",
                "Be careful! A mod must bypass this check for the user to be verified."))
            elif settings["Gamerscore"] == "0":
                return "".join((f"WARNING: {user.mention}'s gamertag exists, but has no gamerscore! ",
                "This is probably a new user, so be careful! A mod must bypass this check for ",
                "the user to be verified."))
            else:
                return "OK"

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def season_add(self, ctx, season, message_id: int):
        try:
            ori_mes = await ctx.guild.get_channel(596186025630498846).fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Invalid message ID! Make sure the message itself is in announcements!")
        ori_timestamp = ori_mes.created_at.timestamp()

        guild_members = ctx.guild.members

        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            season_x_vets = collections.deque()

            for member in guild_members:
                if member.joined_at.timestamp() < ori_timestamp and not member.bot:
                    season_x_vets.append(member)

            for vet in season_x_vets:
                await vet.add_roles(season_x_role)

            await ctx.send(f"Done! Added {len(season_x_vets)} members!")

    @commands.command()
    @commands.check(cogs.cmd_checks.is_gatekeeper_or_up)
    async def verify(self, ctx, member: discord.Member, force = None):
        to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')

        if not to_be_verified in member.roles:
            await ctx.send("This user is already verified!")
            return

        if force != None:
            if force.lower() != "-f":
                await ctx.send("Invalid parameter!")
                return

        if force == None:
            force_txt = "To bypass this check, add '-f' to the end of the command (ex: `!?verify @User#1234 -f`)."

            async with ctx.channel.typing():
                gamertags = discord.utils.get(member.guild.channels, name='gamertags')
                mem_gt_msg = None

                async for message in gamertags.history():
                    if message.author.id == member.id:
                        mem_gt_msg = message
                        break
                
                if mem_gt_msg == None:
                    await ctx.send(f"ERROR: Could not user's gamertag in {gamertags.mention}!\n{force_txt}")
                    return

                status = await self.xbl_handler(mem_gt_msg.content, member)

                if status != "OK":
                    await ctx.send(f"{status}\n{force_txt}")
                    return

        member_role = discord.utils.get(ctx.guild.roles, name='Member')

        await member.remove_roles(to_be_verified)
        await member.add_roles(member_role)

        await ctx.send(f"{member.mention} was verified!")

    @commands.command(aliases=["yeet"])
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def archive(self, ctx):
        if ctx.channel.category.id != 677212464965877803:
            await ctx.send("This isn't the Channel Testing Facility!")
            return

        msg = await ctx.send("Are you sure you want to do this?")
        await msg.add_reaction("✅") # check mark
        await msg.add_reaction("❌") # red x

        def check(reaction, user):
            return user == ctx.author and str(reaction) in ("✅", "❌") and reaction.message.id == msg.id

        async def archive_cancel():
            await msg.delete()

            new_msg = await ctx.edit(content="This command has been cancelled.")
            await asyncio.sleep(5)

            await new_msg.delete()
            await ctx.message.delete()

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await archive_cancel()
        else:
            if str(reaction) == "❌":
                await archive_cancel()
            else:
                archive_cata = discord.utils.find(ctx.guild.categories, id = 683457443996631117) # archive cate
                if archive_cata != None:
                    await msg.delete()

                    action = "Moved"

                    if ctx.invoked_with.lower() == "yeet":
                        action = "Yeeted"

                    await ctx.channel.edit(category=archive_cata, position=0, sync_permissions=True, 
                        reason=f"{action} to The Archives by {str(ctx.author)}.")
                    await ctx.send(f"{action} to The Archives.")

                else:
                    await msg.delete()
                    await ctx.send("I was unable to find The Archives category. Report this to Sonic, this is a glitch.")

def setup(bot):
    bot.add_cog(ModCMDS(bot))
