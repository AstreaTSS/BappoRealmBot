from discord.ext import commands
import discord, datetime

class ETC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            current_time = datetime.datetime.utcnow().timestamp()

            if (current_time - member.created_at.timestamp()) <= 604800:
                try:
                    await member.send("Your account is too young to join the Bappo Realm Discord server. Try "
                    "again once your Discord account is 7 days old.")
                except discord.Forbidden:
                    owner = await self.bot.application_info().owner
                    await owner.send(f"{member.mention} has blocked DMs and is being kicked for having too young of an account.")

                await member.kick(reason="Too young account to join Bappo")
            else:
                gatekeeper = discord.utils.get(member.guild.roles, name='Gatekeeper')

                verify_channel = discord.utils.get(member.guild.channels, name='verify')
                gamertags = discord.utils.get(member.guild.channels, name='gamertags')

                await verify_channel.send("Welcome to the Bappo Realm, " + member.mention + "!\n\nYou might have " +
                "noticed that there's not a lot of channels. Well, that's because you have to be verified. To be verified, " +
                "check out the questions below and answer them here. Also, make sure to put your gamertag in " + gamertags.mention + " so that we " +
                "know who you are in Minecraft.\nA " + gatekeeper.mention + " will review them and verify you.\n\n" +
                "```\nVerification Questions:\n\n 1. How did you come to know about this realm? Don't just say \"advertising\" if that's true " +
                "for you; be more specific, like stating from where.\n\n2. How long have you been playing Minecraft? How long have you been on " +
                "Discord? Have you ever been a problem in Minecraft or Discord?\n\n3. What platform do you play on? Are you aware that this is a " +
                " Bedrock edition realm, not a Java edition realm?\n\n4. What are RULES 2 and 6 in your own words? If you don't understand what this " + 
                "means, explain rules 2 and 6 like you would if explaining it to another person.\n```")

    @commands.Cog.listener()
    async def on_message(self, mes):
        if not mes.guild == None and not mes.author.bot:
            if mes.channel.id == 638566668372541441 or mes.channel.id == 631597319103578122:
                owner_role = mes.guild.get_role(596185339018608641)
                second_owner = mes.guild.get_role(641841757121675264)

                if not owner_role in mes.author.roles:
                    if not second_owner in mes.author.roles:
                        await mes.delete()

def setup(bot):
    bot.add_cog(ETC(bot))