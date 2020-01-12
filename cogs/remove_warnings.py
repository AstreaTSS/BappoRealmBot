from discord.ext import commands
import asyncio, datetime, math
import discord, cogs.cmd_checks

class RemoveWarnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.remove_warnings(True))

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def forcerun_remove_warningsd(self, ctx):
        await self.remove_warnings(False)
        await ctx.send("Done!")

    async def check_and_remove(self, member, role):
        for roles in member.roles:
            if role in roles:
                await member.remove_roles(role)
        
    async def remove_warnings(self, loop):
        go = True

        while go:
            if loop == False:
                go = False
            else:
                current_time = datetime.datetime.utcnow().timestamp()

                multiplicity = math.ceil(current_time / 43200)
                next_twelve = multiplicity * 43200

                sleep_time = next_twelve - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                current_time = datetime.datetime.utcnow().timestamp()
                thirty_days_ago = current_time - 2592000

                guild = self.bot.get_guild(596183975953825792)

                warning_1 = guild.get_role(623546673615994891)
                warning_2 = guild.get_role(623546740917927975)
                warning_3 = guild.get_role(623546743212212236)

                entries = await guild.audit_logs(limit=None, before=thirty_days_ago,
                action=discord.AuditLogAction.member_role_update).flatten()

                for entry in entries:
                    if type(entry.target) is discord.Member and entry.after.roles != None:
                        if warning_1 in entry.after.roles:
                            await self.check_and_remove(entry.target, warning_1)
                        if warning_2 in entry.after.roles:
                            await self.check_and_remove(entry.target, warning_2)
                        if warning_3 in entry.after.roles:
                            await self.check_and_remove(entry.target, warning_3)



def setup(bot):
    bot.add_cog(RemoveWarnings(bot))