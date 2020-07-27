from discord.ext import commands
import asyncio, datetime, math
import discord, cogs.utils

class RemoveWarnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.remove_warnings(True))

    @commands.command()
    @commands.check(cogs.utils.is_mod_or_up)
    async def forcerun_remove_warnings(self, ctx):
        await self.remove_warnings(False)
        await ctx.send("Done!")

    async def check_and_remove(self, member, role):
        if role in member.roles:
            await member.remove_roles(role)
        
    async def remove_warnings(self, loop):
        go = True

        while go:
            if loop == False:
                go = False
            else:
                current_time = datetime.datetime.utcnow().timestamp()

                multiplicity = math.ceil(current_time / 21600)
                next_six = multiplicity * 21600

                sleep_time = next_six - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            current_time = datetime.datetime.utcnow()

            thirty_days = datetime.timedelta(days=30)
            thirty_days_ago = current_time - thirty_days

            thirty_two_days = datetime.timedelta(days=32)
            thirty_two_days_ago = current_time - thirty_two_days

            guild = self.bot.get_guild(596183975953825792)

            warning_1 = guild.get_role(623546673615994891)
            warning_2 = guild.get_role(623546740917927975)
            warning_3 = guild.get_role(623546743212212236)
            warning_roles = [warning_1, warning_2, warning_3]

            members_with_warns = {}

            entries = await guild.audit_logs(limit=None, before=thirty_two_days_ago, after=thirty_days_ago, oldest_first = False, 
            action=discord.AuditLogAction.member_role_update).flatten()

            for entry in entries:
                if type(entry.target) is discord.Member and entry.after.roles != None:
                    if not entry.target in members_with_warns.keys():
                        members_with_warns[entry.target] = []

                    for warning in warning_roles:
                        if warning in entry.after.roles and not warning in members_with_warns[entry.target]:
                            await self.check_and_remove(entry.target, warning)
                            members_with_warns[entry.target].append(warning)

def setup(bot):
    bot.add_cog(RemoveWarnings(bot))