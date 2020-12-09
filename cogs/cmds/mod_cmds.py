from discord.ext import commands
import discord, cogs.utils, re, asyncio, typing
import urllib.parse, aiohttp, os, collections

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

class ModCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def verify_xbl_handler(self, gamertag, user: discord.Member):
        mem_gt_url = gamertag

        async with AuthenticationManager(os.environ.get("XBOX_EMAIL"), os.environ.get("XBOX_PASSWORD")) as auth_mgr:
            async with XboxLiveClient(auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid) as xb_client:
                profile = await xb_client.profile.get_profile_by_gamertag(mem_gt_url)

                try:
                    resp_json = await profile.json()
                except aiohttp.ContentTypeError:
                    return f"ERROR: Unable to find {user.mention}'s gamertag, `{gamertag}`! Make sure it is spelled and entered in correctly!"
                
        if "code" in resp_json.keys():
            return f"ERROR: Unable to find {user.mention}'s gamertag, `{gamertag}`! Make sure it is spelled and entered in correctly!"
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
    @commands.check(cogs.utils.is_mod_or_up)
    async def season_add(self, ctx, season, message_id: typing.Optional[int]):

        if message_id != None:
            try:
                ori_mes = await ctx.guild.get_channel(596186025630498846).fetch_message(message_id)
            except discord.NotFound:
                await ctx.send("Invalid message ID! Make sure the message itself is in announcements!")
            ori_timestamp = ori_mes.created_at.timestamp()
        else:
            ori_timestamp = ctx.message.created_at.timestamp()

        guild_members = ctx.guild.members
        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')

        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            await ctx.send(f"Starting process for S{season}.")

            season_x_vets = collections.deque()

            for member in guild_members:
                if member.joined_at.timestamp() < ori_timestamp and not member.bot:
                    season_x_vets.append(member)

            for vet in season_x_vets:
                await vet.add_roles(season_x_role)
                await asyncio.sleep(1)

            await ctx.send(f"Done! Added {len(season_x_vets)} members!")

    @commands.command()
    @commands.check(cogs.utils.is_gatekeeper_or_up)
    async def verify(self, ctx, member: discord.Member, *args):
        force = False
        member_gamertag = ""

        to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')

        if not to_be_verified in member.roles:
            await ctx.send("This user is already verified!")
            return

        if args:
            if args[0].lower() == "-f":
                force = True
            elif args[0].lower() == "-g":
                member_gamertag = args[1]
            else:
                await ctx.send("That's not a valid argument! There are only two so far, `-f` and `-g`. Please consult to " +
                "the help command to see how to use those.")
                return

        if not force:
            force_txt = "To bypass this check, add '-f' to the end of the command (ex: !?verify @User#1234 -f)."

            async with ctx.channel.typing():
                if member_gamertag == "":
                    gamertags = discord.utils.get(member.guild.channels, name='gamertags')

                    async for message in gamertags.history():
                        if message.author.id == member.id:
                            member_gamertag = message.content
                            break
                    
                    if member_gamertag == "":
                        await ctx.send(f"ERROR: Could not user's gamertag in {gamertags.mention}!\n{force_txt}")
                        return

                status = await self.verify_xbl_handler(member_gamertag, member)

                if status != "OK":
                    await ctx.send(f"{status}\n{force_txt}")
                    return

        member_role = discord.utils.get(ctx.guild.roles, name='Member')

        await member.remove_roles(to_be_verified)
        await member.add_roles(member_role)

        await ctx.send(f"{member.mention} was verified!")

    @commands.command(aliases=["yeet"])
    @commands.check(cogs.utils.is_mod_or_up)
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
                archive_cata = discord.utils.get(ctx.guild.categories, id = 741898424521326594) # archive part 2 cate
                if archive_cata != None:
                    await msg.delete()

                    action = "Moved"

                    if ctx.invoked_with.lower() == "yeet":
                        action = "Yeeted"

                    try:
                        await ctx.channel.edit(category=archive_cata, position=0, sync_permissions=True, 
                            reason=f"{action} to The Archives by {str(ctx.author)}.")
                        await ctx.send(f"{action} to The Archives.")
                        
                    except discord.HTTPException as e:
                        await ctx.send(f"Seems like something went wrong. Here's the error: {e}")

                else:
                    await msg.delete()
                    await ctx.send("I was unable to find The Archives category. Report this to Sonic, this is a glitch.")

def setup(bot):
    bot.add_cog(ModCMDS(bot))
