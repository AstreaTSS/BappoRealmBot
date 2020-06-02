from discord.ext import commands
import discord, cogs.cmd_checks, re
import urllib.parse, aiohttp, os

class ModCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def xbl_handler(self, gamertag, user):
        mem_gt_url = urllib.parse.quote_plus(gamertag)

        headers = {
            "X-Authorization": os.environ.get("OPENXBL_KEY"),
            "Accept": "application/json",
            "Accept-Language": "en-US"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://xbl.io/api/v2/friends/search",params=f"gt={mem_gt_url}") as r:
                resp_json = await r.json()
                if "code" in resp_json.keys():
                    return f"ERROR: Unable to find {user.mention}'s gamertag, {gamertag}!"
                else:
                    settings = {}
                    for setting in resp_json["profileUsers"][0]["settings"]:
                        settings[setting["id"]] = setting["value"]
                    
                    if setting["XboxOneRep"] != "GoodPlayer":
                        return (f"WARNING: {user.mention}'s gamertag exists, but doesn't have the best reputation on Xbox Live! " +
                        "Be careful!A mod must bypass this check for the user to be verified.")
                    elif settings["Gamerscore"] == "0":
                        return (f"WARNING: {user.mention}'s gamertag exists, but has no gamerscore! " +
                        "This is probably a new user, so be careful! A mod must bypass this check for " +
                        "the user to be verified.")
                    else:
                        return "OK"

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def season_add(self, ctx, season, message_id):
        ori_mess = None

        try:
            ori_mess = await ctx.guild.get_channel(596186025630498846).fetch_message(int(message_id))
        except discord.NotFound:
            await ctx.send("Invalid message ID!")
        ori_timestamp = ori_mess.created_at.timestamp()

        guild_members = ctx.guild.members

        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            season_x_vets = []

            for member in guild_members:
                if member.joined_at.timestamp() < ori_timestamp and not member.bot:
                    season_x_vets.append(member)

            for vet in season_x_vets:
                await vet.add_roles(season_x_role)
                print("Added " + vet.display_name)

            await ctx.send("Done! Added " + str(len(season_x_vets)) + " members!")

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def role_id(self, ctx, *role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if role == None:
            await ctx.send("Invalid role name!")
        else:
            await ctx.send(str(role.id))

    @commands.command()
    @commands.check(cogs.cmd_checks.is_gatekeeper_or_up)
    async def verify(self, ctx, member: discord.Member, force = None):
        to_be_verified = discord.utils.get(ctx.guild.roles, name='To Be Verified')
        member_role = discord.utils.get(ctx.guild.roles, name='Member')

        if not to_be_verified in member.roles:
            await ctx.send("This user is already verified!")
            return

        if force != None:
            if force != "-f":
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

        await member.remove_roles(to_be_verified)
        await member.add_roles(member_role)

        await ctx.send(f"{member.mention} was verified!")

def setup(bot):
    bot.add_cog(ModCMDS(bot))
