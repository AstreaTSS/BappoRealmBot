from discord.ext import commands
import discord, random

class ETC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            gatekeeper = discord.utils.get(member.guild.roles, name='Gatekeeper')

            verify_channel = discord.utils.get(member.guild.channels, name='verify')
            gamertags = discord.utils.get(member.guild.channels, name='gamertags')

            verify_start = (f"Welcome to the Bappo Realm, {member.mention}!\n\nYou might have " +
            "noticed that there's not a lot of channels. Well, that's because you have to be verified. " +
            f"To get verified, answer the below questions **and** put your gamertag in {gamertags.mention}. " +
            f"A {gatekeeper.mention} will then verify you.\n\n")

            verify_questions = ("```\nVerification Questions:\n\n" +
            "1. How did you find this Realm?\n\n" +
            "2. Roughly how long have you been playing Minecraft?\n\n" +
            "3. What platform/device do you play on?\n\n" +
            "4. What are RULES 2 and 6 of this server?\n```")

            await verify_channel.send(verify_start + verify_questions)

    @commands.Cog.listener()
    async def on_message(self, mes):
        rand_chance = random.randint(1, 4999)
        if rand_chance == 49:
            await mes.add_reaction("🍍")

def setup(bot):
    bot.add_cog(ETC(bot))