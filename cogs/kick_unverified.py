from discord.ext import commands
import asyncio, datetime, cogs.cmd_checks
import discord, math

class KickUnverified(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.kick_unverified(True))

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def forcerun_kick_unverified(self, ctx):
        await self.kick_unverified(False)
        await ctx.send("Done!")

    async def kick_unverified(self, loop):
        go = True

        while go:
            if loop == False:
                go = False
            else:
                current_time = datetime.datetime.utcnow().timestamp()

                multiplicity = math.ceil(current_time / 28800)
                next_eight = multiplicity * 28800

                sleep_time = next_eight - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            current_time = datetime.datetime.utcnow().timestamp()
            two_days_ago = current_time - 172800

            unverified = []

            guild = self.bot.get_guild(596183975953825792)
            guild_members = guild.members

            unverified_role = discord.utils.get(guild.roles, name="To Be Verified")

            for member in guild_members:
                if unverified_role in member.roles:
                    unverified.append(member)

            for member in unverified:
                if member.joined_at.timestamp() < two_days_ago:
                    try:
                        await member.send("You have taken too long to do the verification questions, and have been kicked for doing so. " +
                        "If you are still interested in joining the Bappo Realm,  please contact the original inviter to get an " +
                        "invite or use the invite you used previously (for security reasons, the bot cannot give you one).")
                    except discord.Forbidden:
                        owner = await self.bot.application_info().owner
                        await owner.send(f"{member.mention} has blocked DMs and is being kicked for not verifying.")

                    await member.kick(reason="Took too long to verify")

def setup(bot):
    bot.add_cog(KickUnverified(bot))