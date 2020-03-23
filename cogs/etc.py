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

            await verify_channel.send("Welcome to the Bappo Realm, " + member.mention + "!\n\nYou might have " +
            "noticed that there's not a lot of channels. Well, that's because you have to be verified. To be verified, " +
            "check out the questions below and answer them here. Also, make sure to put your gamertag in " + gamertags.mention + " so that we " +
            "know who you are in Minecraft.\nA " + gatekeeper.mention + " will review them and verify you.\n\n" +
            "```\nVerification Questions:\n\n1. How did you come to know about this realm? Don't just say \"advertising\" if that's true " +
            "for you; be more specific, like stating from where.\n\n2. How long have you been playing Minecraft? How long have you been on " +
            "Discord? Have you ever been a problem in Minecraft or Discord?\n\n3. What platform do you play on? Are you aware that this is a " +
            " Bedrock edition realm, not a Java edition realm?\n\n4. What are RULES 2 and 6 in your own words? If you don't understand what this " + 
            "means, explain rules 2 and 6 like you would if explaining it to another person.\n```")

    @commands.Cog.listener()
    async def on_message(self, mes):
        rand_chance = random.randint(1, 4999)
        if rand_chance == 49:
            await mes.add_reaction("🍍")

def setup(bot):
    bot.add_cog(ETC(bot))